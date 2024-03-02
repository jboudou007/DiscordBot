import aiohttp
import asyncio
import os
from config import GITHUB_TOKEN, REPO_OWNER, REPO_NAME, BRANCH
from utilities import logger, cache
import base64


# First, we need to fetch the structure of the repository
async def fetch_github_repo_structure(session):
    """Asynchronously fetches the structure of the specified GitHub repository.
    
    Parameters:
    - session: An aiohttp client session for making HTTP requests.
    
    Returns a list of tree objects representing the repository's structure."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"Successfully fetched GitHub repo structure for {REPO_NAME}")
                return data['tree']
            else:
                logger.error(f"Failed to fetch GitHub repo structure. HTTP Status: {response.status}")
                return []
    except Exception as e:
        logger.error(f"Exception occurred while fetching GitHub repo structure: {e}", exc_info=True)
        return []


#feteches the content of a file, which will be used to select relevant files
async def fetch_file_content(session, file_path):
    """
    Asynchronously fetches the content of a specific file from the GitHub repository.
    
    This function checks a local cache before making an HTTP request to GitHub to
    reduce network calls for previously fetched files. It handles binary and non-binary
    files differently, decoding base64 encoded content as necessary.
    
    Parameters:
    - session: An aiohttp client session for making HTTP requests.
    - file_path: The path to the file within the GitHub repository.
    
    Returns:
    - The content of the file as a string, or None for binary files or in case of errors.
    """
    try:
        # Check the local cache first to avoid unnecessary network requests
        if file_path in cache:
            logger.info(f"Fetching file content for {file_path} from cache")
            return cache[file_path]

        # Proceed to fetch from GitHub if not in cache
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}?ref={BRANCH}"
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        
        # Make the asynchronous HTTP request to GitHu
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                # Filter out binary files based on content encoding
                if 'encoding' in data and data['encoding'] == 'base64':
                    try:
                        content = base64.b64decode(data['content']).decode('utf-8')
                        # Update cache
                        cache[file_path] = content
                        logger.info(f"Successfully fetched file content for {file_path}")
                        return content
                    except UnicodeDecodeError:
                        # Log a message and return None for binary or non-UTF-8 encoded files
                        logger.warning(f"Skipping binary or non-UTF-8 file: {file_path}")
                        return None
                else:
                    # Assuming non-base64 encoded data is not what we're looking for
                    logger.warning(f"Skipping non-base64 encoded file: {file_path}")
                    return None
            else:
                logger.error(f"Failed to fetch file content for {file_path}. HTTP Status: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Exception occurred while fetching file content for {file_path}: {e}", exc_info=True)
        return None

#it is good practice to fetch all file contents concurrently

async def fetch_all_file_contents(session, file_paths):
    """
    Fetches the content of multiple files from the GitHub repository concurrently.
    
    This function leverages asyncio.gather to make concurrent HTTP requests to GitHub,
    reducing the total time required to fetch multiple files. It is particularly useful
    for operations that need to retrieve the content of several files in a single go.
    
    Parameters:
    - session: An aiohttp client session for making HTTP requests.
    - file_paths: A list of file paths within the GitHub repository to fetch.
    
    Returns:
    - A list of file contents in the same order as the input file_paths. Each element
      in the list corresponds to the content of the file at the same index in file_paths.
    """
    # Create a list of coroutine objects for fetching each file content
    tasks = [fetch_file_content(session, file_path) for file_path in file_paths]
    # Use asyncio.gather to run all fetch tasks concurrently and wait for all to complete
    return await asyncio.gather(*tasks)
