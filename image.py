import discord
import json
import os
import aiohttp
import asyncio
import tempfile

# Load bot token
TOKEN_FILE = "token.txt"
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()
else:
    TOKEN = input("Enter your Discord bot token: ").strip()

# File paths
POINTS_FILE = "points.json"

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

# Get user's current points
def get_user_points(user_id):
    return points_data.get(str(user_id), 0)

# Update user's points
def update_user_points(user_id, new_points):
    points_data[str(user_id)] = new_points
    save_data(POINTS_FILE, points_data)

# Create intents object and enable the necessary intents
intents = discord.Intents.default()
intents.messages = True  # Enable receiving messages
client = discord.Client(intents=intents)  # Pass the intents to the client

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!image'):
        user_id = str(message.author.id)
        required_points = 1000  # Points needed for image generation
        current_points = get_user_points(user_id)
        
        if current_points < required_points:
            await message.channel.send("You don't have enough points to generate an image.")
            return
        
        # Deduct points and inform user that processing has started
        update_user_points(user_id, current_points - required_points)
        prompt = message.content[len('!image '):].strip()
        
        # Confirm the start of the process
        await message.channel.send("Processing your request to generate an image...")
        
        try:
            generated_image = await generate_image(prompt)
            
            if generated_image:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file.write(generated_image)
                    file_path = temp_file.name
                try:
                    await message.channel.send(file=discord.File(fp=file_path))
                    await message.channel.send("Image successfully generated and sent!")
                finally:
                    os.remove(file_path)  # Clean up the temporary file
            
            else:
                raise Exception("Image generation failed.")
        
        except Exception as e:
            print(f"Error: {e}")
            update_user_points(user_id, current_points)  # Refund points
            await message.channel.send("Failed to generate image. Your points have been refunded.")

async def generate_image(prompt):
    async with aiohttp.ClientSession() as session:
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
        print(f"Generating image with prompt: {prompt}")
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    error_message = await response.text() or "Unknown error occurred."
                    print(f"Failed to generate image. Status code: {response.status}, Response: {error_message}")
                    return None
        except aiohttp.ClientError as e:
            print(f"HTTP request failed: {e}")
            return None

client.run(TOKEN)
