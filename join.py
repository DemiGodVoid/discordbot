import discord
import re
from discord.ext import commands

# Read the token from token.txt
with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Regular expression to match Discord invite links
INVITE_LINK_REGEX = re.compile(r'https?://(?:ptb|canary|www\.)?discord(?:app)?\.com/invite/[a-zA-Z0-9]+')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!join'):
        invite_link = message.content.split(' ')[1]
        if INVITE_LINK_REGEX.match(invite_link):
            try:
                # Join the server using the invite link
                await bot.accept_invite(invite_link)
                await message.channel.send("Joined server successfully")
            except Exception as e:
                await message.channel.send(f"Failed to join server: {e}")
        else:
            await message.channel.send("Invalid invite link")

bot.run(TOKEN)
