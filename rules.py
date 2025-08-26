import discord
import json
from discord.ext import commands

# Load bot token from token.json
def load_token():
    with open("token.json", "r") as file:
        data = json.load(file)
    return data["token"]

# Intents are required to track user join events
intents = discord.Intents.default()
intents.members = True  # Make sure we can track when members join the server

# Create the bot with a command prefix '!'
bot = commands.Bot(command_prefix="!", intents=intents)

# This will store the users that have joined since the bot started
joined_users = set()

# Event to track new members who join the server
@bot.event
async def on_member_join(member):
    joined_users.add(member)

# Command to set the rules
@bot.command()
async def set_rules(ctx, channel_id: int, *, rules: str):
    # Get the channel
    channel = bot.get_channel(channel_id)
    
    if not channel:
        await ctx.send("Invalid channel ID!")
        return

    # Construct the rules message with user tags
    mentioned_users = " ".join([user.mention for user in joined_users])

    # Send the rules along with user mentions
    await channel.send(f"**Rules**:\n{rules}\n\nWelcome {mentioned_users}!")

    # Clear the set of users after sending the rules
    joined_users.clear()

# Start the bot
bot.run(load_token())
