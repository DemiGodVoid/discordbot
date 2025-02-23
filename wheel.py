import discord
import random
import json
import asyncio
from discord.ext import commands

# Load or initialize points data
def load_points():
    try:
        with open("points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_points(data):
    with open("points.json", "w") as f:
        json.dump(data, f, indent=4)

# Load bot token
def load_token():
    try:
        with open("token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return input("Enter your bot token: ")

intents = discord.Intents.default()
intents.messages = True  # Ensures bot can read and send messages
intents.message_content = True  # Enables reading message content
bot = commands.Bot(command_prefix=".", intents=intents)

# Initialize jackpot
def load_jackpot():
    try:
        with open("jackpot.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"amount": 0}

def save_jackpot(data):
    with open("jackpot.json", "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def wheel(ctx):
    user_id = str(ctx.author.id)
    points = load_points()
    jackpot = load_jackpot()

    if user_id not in points:
        points[user_id] = 1000  # Default starting points
    
    if points[user_id] < 500:
        await ctx.send(f"{ctx.author.mention}, you don't have enough points to spin the wheel! Come back when you have at least 500.")
        return

    # Deduct 500 points and add to the jackpot
    points[user_id] -= 500
    jackpot["amount"] += 500
    save_points(points)
    save_jackpot(jackpot)

    messages = [
        f"Win {random.randint(50, 500)}!",
        f"Win {random.randint(500, 5000)}!",
        f"Lose {random.randint(1000, 5000)}",
        f"Jackpot: {jackpot['amount']}"
    ]
    
    msg = await ctx.send(messages[0])
    
    for _ in range(5):
        await asyncio.sleep(1)
        msg_text = random.choice(messages)
        await msg.edit(content=msg_text)
    
    # 2% chance of hitting the jackpot
    if random.randint(1, 100) <= 2:
        final_result = f"Jackpot: {jackpot['amount']}"
        points[user_id] += jackpot["amount"]
        jackpot["amount"] = 0  # Reset jackpot after win
    else:
        final_result = random.choice(messages[:-1])
        amount = int(''.join(filter(str.isdigit, final_result)))
        if "Lose" in final_result:
            points[user_id] -= amount
        else:
            points[user_id] += amount
    
    await msg.edit(content=f'Final Result: {final_result}')
    save_points(points)
    save_jackpot(jackpot)
    await ctx.send(f"{ctx.author.mention}, your new balance is: {points[user_id]} points!")

bot.run(load_token())
