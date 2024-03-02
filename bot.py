import os
import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from text_processing import ask_command_handler

# Initialize Discord bot with specific intents to handle messages and message content
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def ask(ctx, *, question: str):
    """
    Handles the '!ask' command in Discord.
    Invokes the ask_command_handler to process the question.
    
    Parameters:
    - ctx: The context under which the command is executed.
    - question: The user's question input after the command.
    """
    await ask_command_handler(ctx, question)

# Run the bot using the token from the .env file
bot.run(DISCORD_TOKEN)
