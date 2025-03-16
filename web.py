import discord
from discord.ext import commands
import os
import re

# Set up the bot with the required intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

# Path to the tunnel_url.txt file
TUNNEL_URL_PATH = "../server/tunnel_url.txt"  # Adjust the path accordingly

# Function to read bot token from token.txt
def get_bot_token():
    token_file_path = "../discordbot/token.txt"  # Adjust the path to where your token is stored
    if os.path.exists(token_file_path):
        with open(token_file_path, 'r') as token_file:
            return token_file.read().strip()  # Return token without extra spaces
    else:
        print("token.txt file not found!")
        return None

# Command to fetch the tunnel URL
@bot.command()
async def web(ctx):
    # Check if the tunnel_url.txt file exists
    if os.path.exists(TUNNEL_URL_PATH):
        # Open the file and read the contents
        with open(TUNNEL_URL_PATH, 'r') as file:
            content = file.read()

        # Use a regular expression to find all URLs in the file content
        urls = re.findall(r'(https?://\S+)', content)

        # Filter out URLs that contain unwanted keywords
        filtered_urls = [
            url for url in urls
            if "forever-free" not in url and
               "docs" not in url and
               "twitter" not in url and
               "custom-domains" not in url and
               "faq#generating-an-ssh-key" not in url
        ]

        # Keep only the most recent link that ends with 'lhr.life'
        last_lhr_url = None
        for url in reversed(filtered_urls):  # Reverse the list to get the latest first
            if url.endswith("lhr.life"):
                last_lhr_url = url
                break  # Only keep the latest one

        # If a valid last lhr.life URL is found, send it
        if last_lhr_url:
            await ctx.send(f"Our Latest Generated URL: {last_lhr_url}")
        else:
            # If no URLs passed the filter, notify the user
            await ctx.send("No URLs passed the filter.")
    else:
        # If the file doesn't exist, notify the user
        await ctx.send("The file tunnel_url.txt was not found.")

# Read the bot token and run the bot
bot_token = get_bot_token()

if bot_token:
    bot.run(bot_token)
else:
    print("Failed to start the bot because token could not be found.")
