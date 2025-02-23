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
TAKEN_POINTS_FILE = "taken_points.json"

# Load or create points data
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {"total_taken_points": 0}

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

points_data = load_data(POINTS_FILE)
taken_points_data = load_data(TAKEN_POINTS_FILE)

# Get user's current points
def get_user_points(user_id):
    return points_data.get(str(user_id), 0)

# Update user's points
def update_user_points(user_id, new_points):
    points_data[str(user_id)] = new_points
    save_data(POINTS_FILE, points_data)

# Track deducted points
def update_taken_points(points):
    taken_points_data["total_taken_points"] += points
    save_data(TAKEN_POINTS_FILE, taken_points_data)

# Enable required intents
intents = discord.Intents.default()
intents.message_content = True  # Ensure bot can read message content
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('!image'):
        user_id = str(message.author.id)
        required_points = 1000
        current_points = get_user_points(user_id)

        if current_points < required_points:
            await message.channel.send("❌ You don't have enough points to generate an image.")
            return

        # Deduct points and track taken points
        update_user_points(user_id, current_points - required_points)
        update_taken_points(required_points)
        save_data(TAKEN_POINTS_FILE, taken_points_data)

        await message.channel.send(f"✅ 1000 points have been deducted from your account. Remaining balance: {get_user_points(user_id)} points.")

        prompt = message.content[len('!image '):].strip()
        await message.channel.send(f"Generating your image for: **{prompt}** ...")

        try:
            generated_image = await generate_image(prompt)

            if generated_image:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file.write(generated_image)
                    file_path = temp_file.name

                try:
                    with open(file_path, "rb") as f:
                        await message.channel.send(file=discord.File(f, "generated_image.png"))
                    await message.channel.send("✅ Image successfully generated and sent!")
                finally:
                    os.remove(file_path)  # Clean up
            else:
                raise Exception("Image generation failed.")

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("⚠️ An error occurred while processing your request. Please try again later.")

async def generate_image(prompt):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://image.pollinations.ai/prompt/{aiohttp.helpers.quote(prompt)}"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()  # Return image bytes
                else:
                    raise Exception(f"Failed to fetch image: {response.status}")
        except Exception as e:
            print(f"Error in generate_image: {e}")
            return None

# Start the bot
client.run(TOKEN)
