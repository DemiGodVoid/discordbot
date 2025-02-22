import discord
import os
import asyncio
import urllib.parse
import aiohttp
import json

# Function to read or ask for the Discord token
def get_token():
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as file:
            return file.read().strip()
    token = input("Please enter your Discord bot token: ").strip()
    with open("token.txt", "w") as file:
        file.write(token)
    return token

# Function to read or ask for the YouTube API key
def get_youtube_api_key():
    if os.path.exists("youtube_api.txt"):
        with open("youtube_api.txt", "r") as file:
            return file.read().strip()
    api_key = input("Please enter your YouTube API key: ").strip()
    with open("youtube_api.txt", "w") as file:
        file.write(api_key)
    return api_key

# Function to read user points from points.json
def get_user_points(user_id):
    if os.path.exists("points.json"):
        with open("points.json", "r") as file:
            points_data = json.load(file)
        return points_data.get(str(user_id), 0)
    return 0

# Function to update user points in points.json
def update_user_points(user_id, new_points):
    if os.path.exists("points.json"):
        with open("points.json", "r") as file:
            points_data = json.load(file)
    else:
        points_data = {}

    points_data[str(user_id)] = new_points

    with open("points.json", "w") as file:
        json.dump(points_data, file, indent=4)

# Get credentials
TOKEN = get_token()
YOUTUBE_API_KEY = get_youtube_api_key()

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{}"

intents = discord.Intents.default()
intents.message_content = True  
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content == '!commands2':
        embed = discord.Embed(title="Commands", description="List of available commands", color=discord.Color.blue())
        embed.add_field(name="!youtube title - name", value="Search for a YouTube video by title and name.", inline=False)
        embed.add_field(name="!chat prompt", value="Chat with the bot's GPT side! (Takes 500 points per chat)", inline=False)
        embed.add_field(name="!image prompt", value="Generate an image based on a prompt! (1000 points per image)", inline=False)
        embed.add_field(name="!games", value="Access a list of games and point-based activities!", inline=False)
        await message.channel.send(embed=embed)

    if message.content == '!games':
        embed = discord.Embed(title="Bots Games", description="List of available games", color=discord.Color.green())
        embed.add_field(name="!connect4", value="Play connect 4 and win!", inline=False)
        embed.add_field(name=".start_uno", value="Play Uno and gamble!", inline=False)
        embed.add_field(name=".slap_jack", value="Say .slap_help for help!", inline=False)
        embed.add_field(name="!roll amount", value="Gamble your points.", inline=False)
        embed.add_field(name="!spin", value="Spin and get points!", inline=False)
        embed.add_field(name="!pay @user123 amount", value="Give your points to others!", inline=False)
        embed.add_field(name="!bal", value="Check your points.", inline=False)
        embed.add_field(name="!points", value="See everyone's points.", inline=False)
        embed.add_field(name="!giveaway", value="Give away all the points you've taken.", inline=False)
        embed.add_field(name="!taken", value="See the total of taken points people spent.", inline=False)
        embed.add_field(name="----", value="You can earn and spend points in these games!", inline=False)
        await message.channel.send(embed=embed)

    if message.content.startswith('!youtube '):
        query = message.content[len('!youtube '):].strip()
        if query:
            video_url = await search_youtube(query)
            if video_url:
                await message.channel.send(f"Here's the top YouTube result: {video_url}")
            else:
                await message.channel.send("No results found.")
        else:
            await message.channel.send("Please provide a title and name. Example: !youtube Boffy - Pushing minecraft to its limits")
    
    if message.content.startswith('!image '):
        user_id = message.author.id
        points = get_user_points(user_id)

        if points < 1000:
            await message.channel.send(f"Not enough points, please get 1000 points.")
            return
        
        # Deduct 1000 points from the user
        update_user_points(user_id, points - 1000)
        await message.channel.send("1000 points taken successfully")

        prompt = message.content[len('!image '):].strip()
        if prompt:
            image_url = POLLINATIONS_URL.format(urllib.parse.quote(prompt))
            image_path = f"generated_image.png"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        with open(image_path, 'wb') as f:
                            f.write(await resp.read())
                        await message.channel.send(file=discord.File(image_path))
                    else:
                        await message.channel.send("Failed to generate image.")
        else:
            await message.channel.send("Please provide a prompt for the image. Example: !image futuristic city with flying cars")

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
            if 'items' in data and data['items']:
                video_id = data['items'][0]['id']['videoId']
                return f"https://www.youtube.com/watch?v={video_id}"
            return None

client.run(TOKEN)
