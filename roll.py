import discord
import random
import json
from discord.ext import commands

# Function to load the bot token from token.txt
def load_token():
    try:
        with open("token.txt", "r") as f:
            return f.read().strip()  # Strip removes any extra spaces or newline characters
    except FileNotFoundError:
        raise FileNotFoundError("token.txt not found! Please provide a token in the token.txt file.")

# Enable intents
intents = discord.Intents.default()
intents.message_content = True  # Required for message-based commands

# Create a bot instance with command prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# Load points from points.json or create an empty one
def load_points():
    try:
        with open("points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_points(points):
    with open("points.json", "w") as f:
        json.dump(points, f)

# Command: !roll <amount>
@bot.command()
async def roll(ctx, amount: int):
    user_id = str(ctx.author.id)
    user_points = load_points()

    # Check if user has enough points
    current_points = user_points.get(user_id, 0)
    if amount > current_points:
        await ctx.send(f"You don't have enough points! You currently have {current_points} points.")
        return

    # Roll and determine win/loss
    points_won_lost = random.randint(1, 1000)
    result = "won" if random.choice([True, False]) else "lost"
    
    if result == "won":
        # User wins
        user_points[user_id] = current_points + amount + points_won_lost
        await ctx.send(f"You gambled {amount} points and {result}! You gained {points_won_lost} points. Total: {user_points[user_id]} points.")
    else:
        # User loses
        user_points[user_id] = current_points - amount
        await ctx.send(f"You gambled {amount} points and {result}! You lost {amount} points. Total: {user_points[user_id]} points.")
    
    # Save updated points
    save_points(user_points)

# Command: !spin
@bot.command()
async def spin(ctx):
    points = random.randint(1, 3000)

    # Update user points
    user_id = str(ctx.author.id)
    user_points = load_points()
    user_points[user_id] = user_points.get(user_id, 0) + points
    save_points(user_points)

    await ctx.send(f"You spun and gained {points} points!")

# Command: !bal
@bot.command()
async def bal(ctx):
    user_id = str(ctx.author.id)
    user_points = load_points()

    # Get the user's points or 0 if they have no points
    points = user_points.get(user_id, 0)
    await ctx.send(f"You have {points} points.")

# Run the bot
try:
    token = load_token()
    bot.run(token)
except FileNotFoundError as e:
    print(e)
