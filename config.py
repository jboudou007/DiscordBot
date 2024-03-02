from dotenv import load_dotenv
import os

# Load environment variables from .env file for secure access to tokens
load_dotenv()

# Optionally enable asyncio debug mode for detailed coroutine debugging
os.environ['PYTHONASYNCIODEBUG'] = '1'

# Discord, GitHub, and OpenAI API tokens are loaded from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Configuration for the GitHub repository to be accessed by the bot
REPO_OWNER = "PossiblyBobby"
REPO_NAME = "4350_002_Fall23_BucStop"
BRANCH = "Testing"  # Define the branch to work with
