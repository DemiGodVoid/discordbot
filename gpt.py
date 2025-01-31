import discord
from discord.ext import commands
import requests
import os

# Function to get or save the bot token
def get_bot_token():
    token_file = "bot_token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r") as file:
            return file.read().strip()
    else:
        token = input("Enter your bot token: ")
        with open(token_file, "w") as file:
            file.write(token)
        return token

# Set up the bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def chat(ctx, *, message: str):
    """Talk to a free online chatbot!"""
    url = "https://www.pandorabots.com/pandora/talk-xml"
    params = {"botid": "b0dafd24ee35a477", "input": message}
    response = requests.get(url, params=params)
    reply = response.text.split("<that>")[1].split("</that>")[0] if "<that>" in response.text else "I couldn't generate a response."
    await ctx.send(reply)

@bot.command()
async def script(ctx, *, prompt: str):
    """Generate a script using a free online chatbot!"""
    url = "https://www.pandorabots.com/pandora/talk-xml"
    params = {"botid": "b0dafd24ee35a477", "input": f'Write a script about {prompt}'}
    response = requests.get(url, params=params)
    script_text = response.text.split("<that>")[1].split("</that>")[0] if "<that>" in response.text else "I couldn't generate a script."
    await ctx.send(f'```{script_text[:1900]}```')  # Discord message limit

# Run the bot with stored or user-provided token
TOKEN = get_bot_token()
bot.run(TOKEN)
