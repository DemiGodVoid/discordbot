import discord
import requests
import random
import asyncio
import yt_dlp
import os
import time

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# Reddit URLs to fetch short funny videos
REDDIT_URLS = [
    "https://www.reddit.com/r/PublicFreakout.json",
    "https://www.reddit.com/r/FightPorn.json",
    "https://www.reddit.com/r/HolUp.json",
    "https://www.reddit.com/r/AnimalsBeingJerks.json",
    "https://www.reddit.com/r/instant_regret.json"
]

# Global variable to track whether reels should be sent
reels_active = False

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.mkdir(DOWNLOAD_FOLDER)

# Fetch videos from Reddit, ensure they are under 1 minute long
async def fetch_reels():
    videos = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in REDDIT_URLS:
        retries = 3
        for _ in range(retries):
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 429:
                    print("Rate limited. Waiting 5 seconds before retrying...")
                    time.sleep(5)  # Wait for 5 seconds if rate-limited
                    continue
                response.raise_for_status()
                posts = response.json()["data"]["children"]

                for post in posts:
                    if "url" in post["data"] and "v.redd.it" in post["data"]["url"]:
                        video_url = post["data"]["url"]
                        video_length = await get_video_length(video_url)
                        if video_length and video_length <= 60:  # 1 minute = 60 seconds
                            videos.append(video_url)
                break  # Exit the retry loop after a successful request
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from {url}: {e}")
                time.sleep(2)  # Delay on error before retrying
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

    random.shuffle(videos)  # Shuffle to avoid repetition
    return videos

# Get the video length using yt-dlp
async def get_video_length(url):
    ydl_opts = {
        'quiet': True,
        'format': 'bv+ba/b',  # Best video + audio format
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('duration', 0)  # Get duration in seconds
    except Exception as e:
        print(f"Error getting video length for {url}: {e}")
        return None

# Download the video
async def download_video(url):
    filename = f"{random.randint(1000, 9999)}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'outtmpl': filepath,
        'quiet': True,
        'merge_output_format': 'mp4',
        'format': 'bv+ba/b',  # Best video + audio format
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return filepath
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

# Send reels every 60 seconds
async def send_reels(channel):
    while reels_active:
        reels = await fetch_reels()
        if reels:
            captions = [
                "This one had me crying 💀💀💀",
                "Bro not surviving this one 💀🔥",
                "Certified Hood Classic™ 🔥",
                "Bruh what the fuck 😭",
                "WHO TF MADE THIS 💀",
                "Wait for it... 🤣"
            ]
            reel = random.choice(reels)
            video_path = await download_video(reel)
            if video_path:
                await channel.send(random.choice(captions), file=discord.File(video_path))
                os.remove(video_path)  # Remove the file after sending
            else:
                await channel.send("Couldn't download this one 💀")
        await asyncio.sleep(60)  # Wait for 60 seconds before sending the next reel

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    global reels_active

    if message.author == client.user:
        return

    # Trigger to start sending reels
    if message.content.lower() == "!reels_on":
        if not reels_active:
            reels_active = True
            await message.channel.send("🔥 Reels are now ON! Sending funny videos every 60 seconds 🔊💀")
            asyncio.create_task(send_reels(message.channel))
        else:
            await message.channel.send("Reels are already on, fam 😎")

    # Trigger to stop sending reels
    elif message.content.lower() == "!reels_off":
        if reels_active:
            reels_active = False
            await message.channel.send("⚠️ Reels are now OFF. No more funny videos 😭")
        else:
            await message.channel.send("Reels are already off, bro 😐")

# Run the bot with your token
client.run(TOKEN)
