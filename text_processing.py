import aiohttp
from github_integration import fetch_file_content, fetch_github_repo_structure, fetch_all_file_contents  # Adjust import paths as needed
from utilities import logger, get_response_introduction, run_in_executor
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from openai_integration import generate_response_from_summaries
from sklearn.metrics.pairwise import cosine_similarity


# Initialize models and summarizers
model_name = "sentence-transformers/all-MiniLM-L6-v2"
# Initialize Sentence Transformer model
model = SentenceTransformer(model_name)
# You can Initialize the summarization pipeline with BART or another suitable model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


# Here we want to select relevant files based on the user's question using semantic search.
async def select_relevant_files(session, question):
    """
    Identifies relevant files from a GitHub repository based on a semantic search query.
    
    Utilizes the SentenceTransformer model to encode the question and compare it
    against the content of files in the repository to find the most relevant ones.
    
    Parameters:
    - session: aiohttp ClientSession for making HTTP requests.
    - question: User's question in string format.
    
    Returns:
    - A list of file paths deemed most relevant to the question.
    """
    # Attempt to fetch the repository structure and prepare to select relevant files.
    try:
        repo_structure = await fetch_github_repo_structure(session)
        if not repo_structure:
            logger.info("No repo structure found. Skipping file selection.")
            return []

        file_paths = [item['path'] for item in repo_structure if item['type'] == 'blob']

        # Generate question embedding
        question_embedding = model.encode(question)
        
        # Fetch all file contents concurrently
        file_contents = await fetch_all_file_contents(session, file_paths)


        similarities = []
        # Now, file_contents is a list of contents or None (for each file_path)
        for file_path, file_content in zip(file_paths, file_contents):
            try:
                # Fetch file content
                if file_content:
                    # Generate file content embedding
                    file_embedding = model.encode(file_content)
                    # Calculate cosine similarity
                    similarity = cosine_similarity([question_embedding], [file_embedding])[0][0]
                    similarities.append((file_path, similarity))
            except Exception as e:
                print(f"Error fetching file content for {file_path}: {str(e)}")
    except Exception as e:
        print(f"Error selecting relevant files: {str(e)}")
        return []

    # Sort files based on similarity score
    sorted_files = sorted(similarities, key=lambda x: x[1], reverse=True)

    # Select top N files
    relevant_files = [file_path for file_path, _ in sorted_files[:6]]  # Adjust N as needed
    
    logger.info(f"Selected {len(relevant_files)} relevant files based on the question.")

    return relevant_files


async def summarize_file_content(file_content):
    """
    Generates a concise summary of the provided file content using a summarization model.
    
    Parameters:
    - file_content: String content of a file to summarize.
    
    Returns:
    - A string summary of the provided content.
    """
    try:
        # Dynamically adjust max_length based on the input length
        input_length = len(file_content)
        max_length = min(130, max(25, input_length // 4))  # Example heuristic
        summary = summarizer(file_content[:1024], max_length=max_length, min_length=25, do_sample=False)
        logger.info(f"Successfully summarized file content")
        return summary[0]['summary_text']
    except Exception as e:
        logger.error(f"Error summarizing file content: {e}", exc_info=True)
        return None

async def summarize_file_contents(file_content):
    """
    Asynchronously offloads the summarization of file content to a background thread.
    
    Useful for performing CPU-bound summarization tasks without blocking the async event loop.
    
    Parameters:
    - file_content: String content of a file to summarize.
    
    Returns:
    - A summary of the file content as a string.
    """
    return await run_in_executor(blocking_summarize, file_content)


def blocking_summarize(file_content):
    """
    Synchronously generates a summary for the provided file content.
    
    This function is intended to run in a background thread to avoid blocking the
    asynchronous event loop. It wraps the summarization model's synchronous API.
    
    Parameters:
    - file_content: String content of a file to summarize.
    
    Returns:
    - A summary of the file content as a string.
    """
    try:
        # Dynamically adjust max_length based on the input length
        input_length = len(file_content)
        max_length = min(130, max(25, input_length // 4))  # Example heuristic
        summary = summarizer(file_content[:1024], max_length=max_length, min_length=25, do_sample=False)
        logger.info(f"Successfully summarized file content")
        return summary[0]['summary_text']
    except Exception as e:
        logger.error(f"Error summarizing file content: {e}", exc_info=True)
        return None


async def ask_command_handler(ctx, question):
    """
    Handles the '!ask' command within the Discord bot context.
    
    This function orchestrates the process of finding relevant files based on the user's
    question, summarizing their content, and generating a response via the OpenAI API.
    
    Parameters:
    - ctx: The context of the command, containing information like the channel and author.
    - question: The user's question as a string.
    
    Performs the command operation and sends a response message in the Discord channel.
    """
    user = ctx.message.author # here we want to get the user who sent the message
    async with aiohttp.ClientSession() as session:
        try:
            relevant_files = await select_relevant_files(session, question)
            if not relevant_files:
                await ctx.send(f"{user.mention}, I couldn't find relevant files based on your question.")
                return

            aggregated_content = []
            for file_path in relevant_files:
                file_content = await fetch_file_content(session, file_path)
                if file_content:
                    summary = await summarize_file_content(file_content)
                    if summary:
                        aggregated_content.append(f"File: {file_path}\nContent: {summary}\n\n")

            if not aggregated_content:
                await ctx.send(f"{user.mention}, I found relevant files but couldn't retrieve their content.")
                return

            response_message = await generate_response_from_summaries(aggregated_content, question)
            custom_introduction = get_response_introduction(question)
            final_message = f"{user.mention}, {custom_introduction}\n\n{response_message}"

            await ctx.send(final_message[:2000])  # Ensure message does not exceed Discord limit
        except Exception as e:
            logger.error(f"Error processing 'ask' command for user {user}: {e}", exc_info=True)
            await ctx.send(f"{user.mention}, I encountered an error while processing your question.")
            
            