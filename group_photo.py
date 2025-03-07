import discord
import json
import asyncio
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown

# Load Bot Token
def load_token():
    try:
        with open("token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError("token.txt not found! Please provide the bot token.")

# Intents Setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Points Functions
def load_points():
    try:
        with open("points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_points(points):
    with open("points.json", "w") as f:
        json.dump(points, f)

def load_taken_points():
    try:
        with open("taken_points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"total_taken_points": 0}

def save_taken_points(taken_points):
    with open("taken_points.json", "w") as f:
        json.dump(taken_points, f)

# !group_photo Command
@bot.command()
async def group_photo(ctx):
    user_id = str(ctx.author.id)
    user_points = load_points()
    taken_points = load_taken_points()

    current_points = user_points.get(user_id, 0)

    if current_points < 5000:
        await ctx.send(f"{ctx.author.mention} You need **5000 points** to change the group photo.")
        return

    await ctx.send("📸 Please send **media within 20 seconds** to set it as the group profile picture.")

    def check(msg):
        return msg.author == ctx.author and msg.attachments and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", timeout=20, check=check)
        attachment = msg.attachments[0]
        image = await attachment.read()

        # Change Group PFP
        await ctx.guild.edit(icon=image)
        await ctx.send(f"🔥 {ctx.author.mention} changed the **group profile picture** and paid **5000 points!**")

        # Take Points
        user_points[user_id] = current_points - 5000
        taken_points["total_taken_points"] += 5000

        # Save Data
        save_points(user_points)
        save_taken_points(taken_points)

    except asyncio.TimeoutError:
        await ctx.send("❌ You didn't send any media in time.")
    except Exception as e:
        await ctx.send("⚠️ Failed to change group profile picture.")
        print(e)

# Read Messages & Reply
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "hello bot" in message.content.lower():
        await message.channel.send(f"Yo {message.author.mention} 👋")

    await bot.process_commands(message)

# Error Handler
@group_photo.error
async def cooldown_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"You're on cooldown! Try again in {round(error.retry_after, 2)} seconds.")

# Run the Bot
try:
    token = load_token()
    bot.run(token)
except FileNotFoundError as e:
    print(e)
