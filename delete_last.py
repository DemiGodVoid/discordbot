import discord
from discord.ext import commands
import os

# Read token from file
with open("token.txt", "r") as file:
    token = file.read().strip()

intents = discord.Intents.default()
intents.messages = True  # Enable the message intent to interact with messages
intents.guilds = True     # Enable the guilds intent

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def delete_last(ctx):
    # Check if user is admin or owner
    if ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner:
        try:
            # Fetch the last 100 messages in the channel
            messages = await ctx.channel.history(limit=100).flatten()

            # Exclude the command message itself (the first one in the list)
            messages_to_delete = messages[1:]  # All messages except the first one

            if not messages_to_delete:
                await ctx.send("There are no messages to delete.")
                return

            # Delete all messages except the latest one
            await ctx.channel.delete_messages(messages_to_delete)

            # Send a confirmation message
            await ctx.send(f"{len(messages_to_delete)} messages have been deleted!", delete_after=5)  # Delete confirmation after 5 seconds
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"Error: {e}")
    else:
        await ctx.send("You don't have permission to use this command.")

bot.run(token)
