import discord
import os
import asyncio
import urllib.parse
import aiohttp

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
        await message.channel.send('Commands:\n\n!youtube title - name\n!image prompt\n!games')
    
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

            
    if message.content == '!games':
        games_message = """
     Bots Games
     ------
     !connect4 - Play connect 4 and win!
     !roll amount - Gamble
     !spin - Get points!
     ------
     You can earn points and spend it in other games!
        """
        await message.channel.send(games_message)


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
