import discord
import requests
import random
import asyncio
import yt_dlp
import os
import time  # Add time module to handle sleep for rate-limiting

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# Updated list of valid Reddit URLs
REDDIT_URLS = [
    "https://www.reddit.com/r/PublicFreakout.json",
    "https://www.reddit.com/r/FightPorn.json",
    "https://www.reddit.com/r/HolUp.json",
    "https://www.reddit.com/r/AnimalsBeingJerks.json",
    "https://www.reddit.com/r/instant_regret.json",
    "https://www.reddit.com/r/Unexpected.json",
    "https://www.reddit.com/r/WatchPeopleDieInside.json",
    "https://www.reddit.com/r/Memes.json",
    "https://www.reddit.com/r/Funny.json",
    "https://www.reddit.com/r/DankMemes.json",
    "https://www.reddit.com/r/WholesomeMemes.json",
    "https://www.reddit.com/r/ComedyHeaven.json",
    "https://www.reddit.com/r/Trashy.json",
    "https://www.reddit.com/r/PrequelMemes.json",
    "https://www.reddit.com/r/MemeEconomy.json",
    "https://www.reddit.com/r/MemeTemplatesOfficial.json",
    "https://www.reddit.com/r/Teenagers.json",
    "https://www.reddit.com/r/OutOfTheLoop.json"
]

reels_active = {}

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.mkdir(DOWNLOAD_FOLDER)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Handle rate-limiting for all requests
async def fetch_reels():
    videos = []

    for url in REDDIT_URLS:
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                
                if not posts:
                    print(f"No posts found in {url}. Skipping.")
                    continue
                    
                for post in posts:
                    if "url" in post["data"] and "v.redd.it" in post["data"]["url"]:
                        video_data = {
                            'url': post["data"]["url"],
                            'title': post["data"]["title"]
                        }
                        videos.append(video_data)
            elif response.status_code == 429:
                # Handle rate-limiting by waiting
                retry_after = response.headers.get('Retry-After', 60)  # Default to 60 seconds
                print(f"Rate-limited by Reddit for {url}. Retrying in {retry_after} seconds...")
                time.sleep(int(retry_after))  # Wait for the time specified by Reddit
            else:
                print(f"Failed to fetch from {url}: Status Code {response.status_code}")
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
        
        await asyncio.sleep(1)  # Sleep between requests to avoid too many requests in a short period

    random.shuffle(videos)
    return videos

async def download_video(url):
    filename = f"{random.randint(1000, 9999)}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'outtmpl': filepath,
        'quiet': True,
        'merge_output_format': 'mp4',
        'format': 'bv+ba/b',
        'nocheckcertificate': True,  # Disable SSL certificate checking
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return filepath
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

async def check_file_size(file_path):
    file_size = os.path.getsize(file_path)  # Get file size in bytes
    max_size = 8 * 1024 * 1024  # 8 MB for non-Nitro users
    if file_size > max_size:
        return False
    return True

async def send_reels(channel, guild_id):
    while reels_active.get(guild_id, False):
        reels = await fetch_reels()
        if reels:
            reel = random.choice(reels)
            video_url = reel['url']
            title = reel['title']
            video_path = await download_video(video_url)
            if video_path:
                # Check if the video file size is under the limit
                if await check_file_size(video_path):
                    # Use the post title as the caption
                    await channel.send(title, file=discord.File(video_path))
                    os.remove(video_path)
                    await asyncio.sleep(60)  # Wait 60 seconds after sending a video
                else:
                    await channel.send("Video is too large to send. Skipping this one.")
                    os.remove(video_path)  # Remove the large video to avoid unnecessary disk usage
            else:
                await channel.send("Couldn't download this one 💀")
        else:
            await asyncio.sleep(60)  # Wait 60 seconds if there are no available videos to send

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    global reels_active

    if message.author == client.user:
        return

    guild_id = message.guild.id  # Get the guild (server) ID

    if message.content.lower() == "!reels_on":
        if not reels_active.get(guild_id, False):
            reels_active[guild_id] = True
            await message.channel.send("🔥 Reels are now ON! Sending funny ass videos every 60 seconds 🔊💀")
            asyncio.create_task(send_reels(message.channel, guild_id))
        else:
            await message.channel.send("Reels are already on for this server, dumbass 😏")

    elif message.content.lower() == "!reels_off":
        if reels_active.get(guild_id, False):
            reels_active[guild_id] = False
            await message.channel.send("⚠️ Reels are now OFF. No more funny shit 😭")
        else:
            await message.channel.send("Reels are already off for this server, mf 💀")

client.run(TOKEN)
                            
