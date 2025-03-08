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

# This handles the messages before processing commands.
@bot.event
async def on_message(message):
    # Check if the message is from the bot itself to avoid an infinite loop.
    if message.author == bot.user:
        return

    # Log every received message
    print(f"Received message: {message.content}")

    # Now process the command if it exists
    await bot.process_commands(message)

@bot.command()
async def delete_last(ctx):
    print(f"Command received by: {ctx.author}")  # Log who invoked the command

    # Check if the user has admin or owner permissions
    if ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner:
        try:
            # Fetch the last 100 messages in the channel
            print("Fetching messages...")
            messages = await ctx.channel.history(limit=100).flatten()

            print(f"Fetched {len(messages)} messages.")  # Log how many messages were fetched

            # Exclude the command message itself (the first one in the list)
            messages_to_delete = messages[1:]  # All messages except the command itself

            if not messages_to_delete:
                print("No messages to delete.")  # Log if there are no messages to delete
                await ctx.send("There are no messages to delete.")
                return

            # Delete all the messages except the last one
            await ctx.channel.delete_messages(messages_to_delete)

            # Send a confirmation message
            await ctx.send(f"{len(messages_to_delete)} messages have been deleted!", delete_after=5)  # Confirmation message for 5 seconds
            print(f"Deleted {len(messages_to_delete)} messages.")  # Log how many messages were deleted
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"Error: {e}")
    else:
        await ctx.send("You don't have permission to use this command.")

bot.run(token)
