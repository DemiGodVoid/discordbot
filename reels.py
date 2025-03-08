import discord
import requests
import random
import asyncio
import aiohttp
import aiofiles
import os
import yt_dlp

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

REDDIT_URLS = [
    "https://www.reddit.com/r/PublicFreakout.json",
    "https://www.reddit.com/r/FightPorn.json",
    "https://www.reddit.com/r/HolUp.json",
    "https://www.reddit.com/r/AnimalsBeingJerks.json",
    "https://www.reddit.com/r/instant_regret.json"
]

reels_active = False

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.mkdir(DOWNLOAD_FOLDER)

async def fetch_reels():
    videos = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in REDDIT_URLS:
        try:
            response = requests.get(url, headers=headers).json()
            posts = response["data"]["children"]

            for post in posts:
                if "url" in post["data"] and "v.redd.it" in post["data"]["url"]:
                    videos.append(post["data"]["url"])
        except Exception as e:
            print(f"Error fetching from {url}: {e}")

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

# Check the file size before sending
async def check_file_size(file_path):
    file_size = os.path.getsize(file_path)  # Get file size in bytes
    max_size = 8 * 1024 * 1024  # 8 MB for non-Nitro users
    if file_size > max_size:
        return False
    return True

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
                # Check if the video file size is under the limit
                if await check_file_size(video_path):
                    await channel.send(random.choice(captions), file=discord.File(video_path))
                    os.remove(video_path)
                else:
                    await channel.send("Video is too large to send. Skipping this one.")
            else:
                await channel.send("Couldn't download this one 💀")
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    global reels_active

    if message.author == client.user:
        return

    if message.content.lower() == "!reels_on":
        if not reels_active:
            reels_active = True
            await message.channel.send("🔥 Reels are now ON! Sending funny ass videos every 60 seconds 🔊💀")
            asyncio.create_task(send_reels(message.channel))
        else:
            await message.channel.send("Reels are already on, dumbass 😏")

    elif message.content.lower() == "!reels_off":
        if reels_active:
            reels_active = False
            await message.channel.send("⚠️ Reels are now OFF. No more funny shit 😭")
        else:
            await message.channel.send("Reels are already off, mf 💀")

client.run(TOKEN)
