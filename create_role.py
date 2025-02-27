import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to read JSON file
def read_json(file):
    with open(file, 'r') as f:
        return json.load(f)

# Function to write JSON file
def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

@bot.command()
async def create_role(ctx, role_name: str, role_color: str):
    user_id = str(ctx.author.id)
    points = read_json("points.json")
    taken_points = read_json("taken_points.json")

    # Check if user has enough points
    if user_id not in points or points[user_id] < 5000:
        await ctx.send("You need 5k points to use this, say !games and play a game to get points.")
        return

    # Remove 5k points and update points
    points[user_id] -= 5000
    write_json("points.json", points)

    # Add to taken points
    taken_points["total_taken_points"] = taken_points.get("total_taken_points", 0) + 5000
    write_json("taken_points.json", taken_points)

    # Convert role color to discord color
    try:
        color = discord.Color(int(role_color.strip("#"), 16))
    except ValueError:
        await ctx.send("Invalid color code. Use hex codes like #ff0000")
        return

    # Create role and assign to user
    guild = ctx.guild
    role = await guild.create_role(name=role_name, colour=color)
    await ctx.author.add_roles(role)

    await ctx.send(f"Role **{role_name}** created and assigned to you!")

@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")

with open("token.txt", "r") as token_file:
    bot_token = token_file.read().strip()
bot.run(bot_token)
