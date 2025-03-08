import discord
import requests
import random
import asyncio

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

# Global variable to track whether reels should be sent
reels_active = False

async def fetch_reels():
    videos = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in REDDIT_URLS:
        try:
            response = requests.get(url, headers=headers).json()
            posts = response["data"]["children"]

            for post in posts:
                if "url" in post["data"] and "v.redd.it" in post["data"]["url"]:
                    videos.append(post["data"]["url"] + "/DASH_720.mp4")
        except:
            pass

    random.shuffle(videos)  # Shuffling the list to avoid sending the same ones
    return videos

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
            reel = random.choice(reels)  # Choose a random video
            await channel.send(random.choice(captions) + "\n" + reel)
        await asyncio.sleep(60)  # Wait for 60 seconds before sending the next reel

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
            await message.channel.send("🔥 Reels are now ON! Sending fresh ones every 60 seconds 🔥")
            # Start sending reels every 60 seconds
            asyncio.create_task(send_reels(message.channel))
        else:
            await message.channel.send("Reels are already on, fam 😎")

    elif message.content.lower() == "!reels_off":
        if reels_active:
            reels_active = False
            await message.channel.send("⚠️ Reels are now OFF. No more funny videos 😭")
        else:
            await message.channel.send("Reels are already off, bro 😐")

client.run(TOKEN)
      
