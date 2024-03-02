# DiscordBot For a Github Repository

This Discord bot provides insights into GitHub repositories by answering user queries directly within Discord. It uses the GitHub API to fetch repository information, the OpenAI API for natural language understanding and response generation, and integrates semantic search to find relevant files within a GitHub repository.

## Features

- **Semantic Search:** Finds relevant files in a GitHub repository based on user queries.
- **Summarization:** Summarizes content of the files to provide quick insights.
- **OpenAI Integration:** Uses OpenAI's powerful models to generate informative and contextually relevant responses based on the summaries.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.8 or higher is needed: https://www.python.org/downloads/

- Get a Discord Bot Token by following this link, and make sure you invite the bot to your server: https://discordgsm.com/guide/how-to-get-a-discord-bot-token

- Get a GitHub API Token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

- Get an OpenAI API Key: https://platform.openai.com/api-keys

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/jboudou007/DiscordBot.git
```

```bash
cd DiscordBot
```

2. **Set up a virtual environment (optional but highly recommended):**

```bash
python -m venv venv
```

### On Windows

```bash
venv\Scripts\activate
```

### On Unix or MacOS

```bash
source venv/bin/activate
```

3. **Install the dependencies:**

```bash
pip install -r requirements.txt
```

or

```bash
pip install discord.py aiohttp python-dotenv sentence-transformers sklearn numpy cachetools

```

Note: make sure pip is ugraded

```bash
python.exe -m pip install --upgrade pip
```

## Configuration

**Environment Variables:**

Create a _.env_ file in the root directory of the project and add your Discord Bot Token, GitHub API Token, and OpenAI API Key:

```bash
DISCORD_TOKEN=your_discord_bot_token
GITHUB_TOKEN=your_github_api_token
OPENAI_API_KEY=your_openai_api_key
```

**Update Repository Information**
In config.py, update the REPO_OWNER, REPO_NAME, and BRANCH variables to point to the GitHub repository you want the bot to analyze.

## Running the Bot

```bash
python bot.py
```

## Usage

Asking Questions: Use the $!ask$ command followed by your question about the GitHub repository in a Discord channel where the bot is present.

Example:

```bash
!ask tell me everything I need to know about this repo as a first time user
```

## Contributing

Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

MIT

## Contact

If you have any questions or feedback, please contact me at jeanbilong01@gmail.com or on Discord @jboudou007
