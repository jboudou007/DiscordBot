import aiohttp
from config import OPENAI_API_KEY  # Adjust the import path as needed
from utilities import logger

async def generate_response_from_summaries(aggregated_content, question):
    """
    Uses the OpenAI API to generate a response based on the summaries and the question.
    make sure to review the OpenAI API documentation for the latest information.
    
    Generates a response from OpenAI's API based on aggregated content summaries and a user question.

    This function constructs a chat prompt combining summaries of multiple relevant files from a GitHub
    repository with the user's question. It then queries OpenAI's API to generate a response that aims
    to be helpful and informative based on the provided context.

    Parameters:
    - aggregated_content: A list of strings, where each string is a summary of content from a relevant file.
    - question: The user's question as a string.

    Returns:
    - A string containing OpenAI's response if the API call was successful.
    - An error message string if the API call failed.

    Notes:
    - The function utilizes the OpenAI API key defined in the project's configuration.
    - It logs an error message if the API call fails for easier debugging.
    - Review the OpenAI API documentation for the latest information on usage limits and API capabilities.
    """
    
    #construct the chat prompt for OpenAI's API
    chat_prompt = f"You are a helpful assistant. The key information is based on the content summaries from multiple files related to the user's question about the GitHub repository. Here are the summaries:\n\n{''.join(aggregated_content)}\n\nQuestion: {question}"
    
    #Define the payload
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": chat_prompt}
    ]

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    #Make the asynchronous HTTP request to OpenAI's API
    async with aiohttp.ClientSession() as session:
        response = await session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        if response.status == 200:
            openai_data = await response.json()
            answer_text = openai_data['choices'][0]['message']['content']
            return answer_text
        else:
            error_message = await response.text()
            logger.error(f"OpenAI API error: {error_message}")
            return f"I encountered an error with the OpenAI API: {error_message}"


