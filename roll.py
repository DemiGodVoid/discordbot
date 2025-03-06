import discord
import random
import json
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown

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

# Load taken points from taken_points.json or create an empty one
def load_taken_points():
    try:
        with open("taken_points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"total_taken_points": 0}

def save_taken_points(taken_points):
    with open("taken_points.json", "w") as f:
        json.dump(taken_points, f)

# Command: !roll <amount>
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)  # 1 use per 60 seconds per user
async def roll(ctx, amount: int):
    if amount <= 0:  # Prevent negative or zero bets
        await ctx.send("Invalid amount! You must bet a positive number of points.")
        return

    user_id = str(ctx.author.id)
    user_points = load_points()

    # Check if user has enough points
    current_points = user_points.get(user_id, 0)
    if amount > current_points:
        await ctx.send(f"You don't have enough points! You currently have {current_points} points.")
        return

    # Load the taken points from taken_points.json
    taken_points = load_taken_points()

    # 50/50 win/loss
    if random.choice([True, False]):
        # User wins: double the bet
        winnings = amount * 2
        user_points[user_id] = current_points + winnings
        await ctx.send(f"You gambled {amount} points and **won**! You gained {winnings} points. Total: {user_points[user_id]} points.")
    else:
        # User loses: lose the bet
        user_points[user_id] = current_points - amount
        taken_points["total_taken_points"] += amount  # Add lost points to the total taken points
        await ctx.send(f"You gambled {amount} points and **lost**! You lost {amount} points. Total: {user_points[user_id]} points.")

    # Save updated points and taken points
    save_points(user_points)
    save_taken_points(taken_points)

# Command: !spin
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)  # 1 use per 60 seconds per user
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

# Command: !pay @user123 amount
@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    user_id = str(ctx.author.id)
    recipient_id = str(member.id)
    user_points = load_points()

    # Prevent negative or zero transactions
    if amount <= 0:
        await ctx.send("Invalid amount! You must send a positive number of points.")
        return

    # Check if the user has enough points
    current_points = user_points.get(user_id, 0)
    if amount > current_points:
        await ctx.send("Not enough points!")
        return

    # Transfer points
    user_points[user_id] = current_points - amount
    recipient_points = user_points.get(recipient_id, 0)
    user_points[recipient_id] = recipient_points + amount

    # Save updated points
    save_points(user_points)

    # Inform the users
    await ctx.send(f"{ctx.author.mention} has transferred {amount} points to {member.mention}.")

# Error handler for cooldown
@roll.error
@spin.error
async def cooldown_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"You're on cooldown! Please try again in {round(error.retry_after, 2)} seconds.")

# Run the bot
try:
    token = load_token()
    bot.run(token)
except FileNotFoundError as e:
    print(e)
                  
