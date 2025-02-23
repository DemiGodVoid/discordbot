import discord
import json
import os
import asyncio
import aiohttp

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required to detect member joins
client = discord.Client(intents=intents)

# Load or request bot token
TOKEN_FILE = "token.txt"

if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()
else:
    TOKEN = input("Please enter your Discord bot token: ").strip()
    with open(TOKEN_FILE, "w") as f:
        f.write(TOKEN)

# File paths
TRIGGERS_FILE = "triggers.json"
RULES_FILE = "rules.json"
POINTS_FILE = "points.json"
TAKEN_POINTS_FILE = "taken_points.json"

# Load data functions
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Load triggers and rules
triggers = load_data(TRIGGERS_FILE)
rules = load_data(RULES_FILE)
points_data = load_data(POINTS_FILE)
taken_points = load_data(TAKEN_POINTS_FILE)

def get_user_points(user_id):
    return points_data.get(str(user_id), 0)

def update_user_points(user_id, new_points):
    points_data[str(user_id)] = new_points
    save_data(POINTS_FILE, points_data)

def update_taken_points(used_points):
    taken_points["total_taken_points"] = taken_points.get("total_taken_points", 0) + used_points
    save_data(TAKEN_POINTS_FILE, taken_points)

async def generate_image(prompt):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://image.pollinations.ai/prompt/{prompt}") as response:
            if response.status == 200:
                return response.url
            return None

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    if guild_id in rules and rules[guild_id]:
        rule_message = f"Welcome to **{member.guild.name}**, {member.mention}!\n\n**Server Rules:**\n{rules[guild_id]}"
        await member.send(rule_message)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    guild_id = str(message.guild.id)

    if message.content == '!rules':
        if guild_id in rules and rules[guild_id]:
            await message.channel.send(f"**Server Rules:**\n{rules[guild_id]}")
        else:
            await message.channel.send("No rules have been set for this server.")

    if message.content.startswith('!set_rules '):
        if message.author.guild_permissions.administrator:
            new_rules = message.content[len('!set_rules '):].strip()
            rules[guild_id] = new_rules
            save_data(RULES_FILE, rules)
            await message.channel.send("Server rules updated successfully!")
        else:
            await message.channel.send("You do not have permission to set rules.")

    if message.content == '!commands':
        embed = discord.Embed(title="Commands", description="List of available commands", color=discord.Color.blue())
        embed.add_field(name="!rules", value="View server Rules", inline=False)
        embed.add_field(name="!set_rules", value="Set server Rules (Admin only)", inline=False)
        embed.add_field(name="!games", value="List available games", inline=False)
        embed.add_field(name="!commands2", value="View more commands", inline=False)
        await message.channel.send(embed=embed)

    if message.content == '!commands2':
        embed = discord.Embed(title="More Commands", description="Additional fun and utility commands", color=discord.Color.blue())
        embed.add_field(name="!youtube title - name", value="Search for a YouTube video.", inline=False)
        embed.add_field(name="!image prompt", value="Generate an image (1000 points per image).", inline=False)
        embed.add_field(name="!chat prompt", value="Chat with GPT (500 points per chat).", inline=False)
        await message.channel.send(embed=embed)

    if message.content.startswith('!image '):
        user_id = str(message.author.id)
        if get_user_points(user_id) >= 1000:
            prompt = message.content[len('!image '):].strip()
            image_url = await generate_image(prompt)
            if image_url:
                update_user_points(user_id, get_user_points(user_id) - 1000)
                update_taken_points(1000)
                await message.channel.send(f"Here is your generated image: {image_url}")
            else:
                await message.channel.send("Failed to generate image.")
        else:
            await message.channel.send("You do not have enough points.")

    if message.content == '!games':
        embed = discord.Embed(title="Bots Games", description="List of available games", color=discord.Color.green())
        embed.add_field(name="!connect4", value="Play Connect 4!", inline=False)
        embed.add_field(name=".wheel", value="Spin the wheel!", inline=False)
        embed.add_field(name=".start_uno", value="Play Uno!", inline=False)
        embed.add_field(name="!roll amount", value="Gamble points.", inline=False)
        embed.add_field(name="!bal", value="Check your points.", inline=False)
        embed.add_field(name="!points", value="See all points.", inline=False)
        embed.add_field(name="!giveaway", value="Giveaway points.", inline=False)
        embed.add_field(name="!taken", value="Total spent points.", inline=False)
        await message.channel.send(embed=embed)

client.run(TOKEN)
