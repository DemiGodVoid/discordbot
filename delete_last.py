import discord
from discord.ext import commands
import os

# Load token from token.txt file
def get_token():
    with open("token.txt", "r") as file:
        return file.read().strip()

# Define the bot with a command prefix
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Command to delete the last N messages, restricted to admins
@bot.command()
async def delete_last(ctx, number: int):
    # Check if the user has admin permissions
    if ctx.author.guild_permissions.administrator:
        try:
            # Fetch the last 'number' messages before the current message
            deleted = await ctx.channel.purge(limit=number+1)  # Including the command message itself
            await ctx.send(f'Deleted {len(deleted)-1} messages.', delete_after=5)
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
    else:
        # Inform the user if they do not have permission
        await ctx.send("You do not have permission to use this command.", delete_after=5)

# Run the bot using the token from the file
token = get_token()
bot.run(token)
