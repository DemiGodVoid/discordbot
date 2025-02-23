import discord
import json
import os
import aiohttp

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Load bot token
TOKEN_FILE = "token.txt"
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()
else:
    TOKEN = input("Enter your Discord bot token: ").strip()
    with open(TOKEN_FILE, "w") as f:
        f.write(TOKEN)

# File paths
POINTS_FILE = "points.json"
TAKEN_POINTS_FILE = "taken_points.json"

# Load or create points data
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

points_data = load_data(POINTS_FILE)
taken_points = load_data(TAKEN_POINTS_FILE)

# Get user's current points
def get_user_points(user_id):
    return points_data.get(str(user_id), 0)

# Update user's points
def update_user_points(user_id, new_points):
    points_data[str(user_id)] = new_points
    save_data(POINTS_FILE, points_data)

# Update total taken points
def update_taken_points(used_points):
    taken_points["total_taken_points"] = taken_points.get("total_taken_points", 0) + used_points
    save_data(TAKEN_POINTS_FILE, taken_points)

# Generate AI image using Pollinations AI with retry mechanism
async def generate_image(prompt, retries=3):
    async with aiohttp.ClientSession() as session:
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
        print(f"Generating image with prompt: {prompt}")
        
        for attempt in range(retries):
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()  # Pollinations directly returns an image
                else:
                    print(f"Error generating image. Status code: {response.status}. Attempt {attempt+1}/{retries}")
            
            if attempt < retries - 1:
                await asyncio.sleep(2)  # Wait for 2 seconds before retrying
            
        return None

# Bot ready event
@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

# Message command handling
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!image '):
        user_id = str(message.author.id)
        current_points = get_user_points(user_id)
        if current_points >= 1000:
            prompt = message.content[len('!image '):].strip()
            await message.channel.send("⏳ Generating your image, please wait...")
            image_url = await generate_image(prompt)
            if image_url:
                update_user_points(user_id, current_points - 1000)
                update_taken_points(1000)
                await message.channel.send(f"✅ Deducted 1000 points.\nHere is your AI-generated image:\n{image_url}")
            else:
                await message.channel.send("❌ Image generation failed. Please try again later.")
        else:
            await message.channel.send("❌ You do not have enough points.")

client.run(TOKEN)
