import discord
import json
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown

# Function to load the bot token from token.txt
def load_token():
    try:
        with open("token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError("token.txt not found! Please provide the bot token.")

# Enable intents
intents = discord.Intents.default()
intents.message_content = True  # Needed to read messages
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load points
def load_points():
    try:
        with open("points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_points(points):
    with open("points.json", "w") as f:
        json.dump(points, f)

# Load taken points
def load_taken_points():
    try:
        with open("taken_points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"total_taken_points": 0}

def save_taken_points(taken_points):
    with open("taken_points.json", "w") as f:
        json.dump(taken_points, f)

# Command: !group_name MESSAGE
@bot.command()
async def group_name(ctx, *, new_name: str):
    user_id = str(ctx.author.id)
    user_points = load_points()
    taken_points = load_taken_points()

    current_points = user_points.get(user_id, 0)

    # Check if user has enough points
    if current_points < 5000:
        await ctx.send(f"{ctx.author.mention} You don't have enough points! You need 5000 points.")
        return

    # Take 5000 points
    user_points[user_id] = current_points - 5000
    taken_points["total_taken_points"] += 5000

    # Save updated points
    save_points(user_points)
    save_taken_points(taken_points)

    # Change group name (server name)
    try:
        await ctx.guild.edit(name=new_name)
        await ctx.send(f"🔔 {ctx.author.mention} changed the group name to **{new_name}** and paid **5000 points!**")
    except Exception as e:
        await ctx.send("Failed to change group name.")
        print(e)

# Read Messages and Reply
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "hello bot" in message.content.lower():
        await message.channel.send(f"Hello {message.author.mention}!")

    await bot.process_commands(message)

# Error Handler
@group_name.error
async def cooldown_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"You're on cooldown! Try again in {round(error.retry_after, 2)} seconds.")

# Run the bot
try:
    token = load_token()
    bot.run(token)
except FileNotFoundError as e:
    print(e)
