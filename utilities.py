from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor
import logging
import asyncio

# A cache is initialized to store up to 100 items with each item expiring after an hour (3600 seconds).
# This cache is used to temporarily store data that is expensive to compute or retrieve,
# such as responses from external API calls or computation-heavy results.
cache = TTLCache(maxsize=100, ttl=3600)

# A ThreadPoolExecutor is initialized for running blocking IO-bound tasks in a background thread.
# This allows the asynchronous event loop to remain responsive by offloading blocking operations
# to separate threads. This is particularly useful for operations like file IO or network requests
# that do not have asynchronous interfaces.
executor = ThreadPoolExecutor(max_workers=5)

# Basic logging configuration is set up to log informational messages and above (INFO, WARNING, ERROR, CRITICAL).
# The logging format includes the timestamp, logger name, log level, and the log message, providing a standardized
# logging output for debugging and monitoring purposes.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# A logger instance is created with the module's name. This allows for module-specific logging configurations
# and makes it easier to trace log messages back to their source.
logger = logging.getLogger(__name__)

def get_response_introduction(question):
    """
    Generates an introduction response based on the content of a user's question.
    
    This function aims to provide a contextually appropriate introduction to the bot's response,
    enhancing the user's interaction experience by tailoring the response to the nature of the question.
    
    Parameters:
    - question: A string containing the user's question.
    
    Returns:
    - A string containing an introduction tailored to the question's context.
    """
    if "where is" in question.lower() or "how do I find" in question.lower():
        return "Here's what you're looking for:"
    elif "improvements" in question.lower() or "how can we improve" in question.lower():
        return "Here are some suggestions for improvements:"
    elif "explain" in question.lower() or "what is" in question.lower():
        return "Let me explain that for you:"
    else:
        return "Based on your question, here's what I found:"

async def run_in_executor(func, *args):
    """
    Runs a blocking function in a background thread, allowing asyncio coroutines to remain unblocked.
    
    This function is particularly useful for executing IO-bound or CPU-bound functions that do not support
    asynchronous execution natively. It leverages asyncio's event loop to run these functions in a ThreadPoolExecutor,
    ensuring that the main async flow is not disrupted.
    
    Parameters:
    - func: The blocking function to execute.
    - *args: Variable length argument list for the blocking function.
    
    Returns:
    - The result of the blocking function's execution.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, func, *args)
