import discord
import json
import os
import aiohttp
import asyncio
import urllib.parse

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required to detect member joins
client = discord.Client(intents=intents)

# Load or request bot token
TOKEN_FILE = "token.txt"
YOUTUBE_API_FILE = "youtube_api.txt"

if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()
else:
    TOKEN = input("Please enter your Discord bot token: ").strip()
    with open(TOKEN_FILE, "w") as f:
        f.write(TOKEN)

if os.path.exists(YOUTUBE_API_FILE):
    with open(YOUTUBE_API_FILE, "r") as f:
        YOUTUBE_API_KEY = f.read().strip()
else:
    YOUTUBE_API_KEY = input("Please enter your YouTube API key: ").strip()
    with open(YOUTUBE_API_FILE, "w") as f:
        f.write(YOUTUBE_API_KEY)

# File paths
TRIGGERS_FILE = "triggers.json"
RULES_FILE = "rules.json"
POINTS_FILE = "points.json"
TAKEN_POINTS_FILE = "taken_points.json"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{}"

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

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    if guild_id in rules and rules[guild_id]:
        rule_message = f"Welcome to **{member.guild.name}**, {member.mention}!\n\n**Server Rules:**\n{rules[guild_id]}"
        for channel in member.guild.text_channels:
            if channel.permissions_for(member.guild.me).send_messages:
                await channel.send(rule_message)
                break

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    guild_id = str(message.guild.id)
    msg_lower = message.content.lower()

    if msg_lower in triggers.get(guild_id, {}):
        await message.channel.send(triggers[guild_id][msg_lower])

    if message.content == '!ping':
        await message.channel.send('PONG')

    if message.content == '!commands':
        await message.channel.send(
            'Commands:\n\n!ping\n\n!gif message (send a related GIF)\n\n'
            '!trigger message=message (set a trigger response)\n\n'
            '!set_rules message (set server rules)\n\n!rules (view server rules)\n\n!commands2 (More commands)'
        )

    if message.content == '!commands2':
        embed = discord.Embed(title="Commands", description="List of available commands", color=discord.Color.blue())
        embed.add_field(name="!youtube title - name", value="Search for a YouTube video.", inline=False)
        embed.add_field(name="!chat prompt", value="Chat with GPT (500 points per chat).", inline=False)
        embed.add_field(name="!image prompt", value="Generate an image (1000 points per image).", inline=False)
        embed.add_field(name="!games", value="List of games.", inline=False)
        await message.channel.send(embed=embed)

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

    if message.content.startswith('!youtube '):
        query = message.content[len('!youtube '):].strip()
        video_url = await search_youtube(query)
        await message.channel.send(video_url if video_url else "No results found.")

    if message.content.startswith('!image '):
        user_id = message.author.id
        if get_user_points(user_id) < 1000:
            await message.channel.send("Not enough points.")
            return
        update_user_points(user_id, get_user_points(user_id) - 1000)
        update_taken_points(1000)
        prompt = message.content[len('!image '):].strip()
        image_url = POLLINATIONS_URL.format(urllib.parse.quote(prompt))
        await message.channel.send(image_url)

async def search_youtube(query):
    async with aiohttp.ClientSession() as session:
        async with session.get(YOUTUBE_SEARCH_URL, params={
            'part': 'snippet',
            'q': query,
            'key': YOUTUBE_API_KEY,
            'maxResults': 1,
            'type': 'video'
        }) as response:
            data = await response.json()
            return f"https://www.youtube.com/watch?v={data['items'][0]['id']['videoId']}" if 'items' in data and data['items'] else None

client.run(TOKEN)
