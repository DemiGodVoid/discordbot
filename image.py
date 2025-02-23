import discord
import json
import os
import aiohttp
import asyncio

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
                    return await response.read()  # Return the raw bytes of the image
                else:
                    print(f"Error generating image. Status code: {response.status}. Attempt {attempt+1}/{retries}")
            
            if attempt < retries - 1:
                await asyncio.sleep(2)  # Wait for 2 seconds before retrying
            
        return None

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!image'):
        prompt = message.content[len('!image'):].strip()
        if not prompt:
            await message.channel.send("Please provide a prompt after the command.")
            return
        
        # Deduct 1000 points from the user
        user_id = str(message.author.id)
        current_points = get_user_points(user_id)
        if current_points < 1000:
            await message.channel.send("You don't have enough points to generate an image. You need at least 1000 points.")
            return
        
        new_points = current_points - 1000
        update_user_points(user_id, new_points)
        update_taken_points(1000)

        # Generate and send the image
        image_content = await generate_image(prompt)
        if image_content:
            # Send the image as a file attachment
            await message.channel.send(file=discord.File(fp=image_content, filename="generated_image.png"))
            await message.author.send(f"Successfully deducted 1000 points from your account. You now have {new_points} points remaining.")
        else:
            update_user_points(user_id, current_points)  # Refund the points if image generation fails
            update_taken_points(-1000)
            await message.channel.send("❌ Unable to generate image. Please try again later.")

client.run(TOKEN)
