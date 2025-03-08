import discord
from discord.ext import commands
import os

# Read token from file
with open("token.txt", "r") as file:
    token = file.read().strip()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def delete_last(ctx):
    # Check if user is admin or owner
    if ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner:
        messages = await ctx.channel.history(limit=100).flatten()
        count = len(messages) - 1  # Exclude the command message itself
        await ctx.channel.delete_messages(messages[1:])  # Delete all but the last one

        # Send a confirmation message
        await ctx.send(f"{count} messages have been deleted!", delete_after=5)  # Delete confirmation after 5 seconds
    else:
        await ctx.send("You don't have permission to use this command.")

bot.run(token)
