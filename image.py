import discord
import json
import os
import aiohttp
import asyncio
import time
import io

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

# Load JSON data (always fresh)
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

# Save JSON data
def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Get user's current points
def get_user_points(user_id):
    points_data = load_data(POINTS_FILE)
    return points_data.get(str(user_id), 0)

# Update user's points
def update_user_points(user_id, new_points):
    points_data = load_data(POINTS_FILE)
    points_data[str(user_id)] = new_points
    save_data(POINTS_FILE, points_data)

# Track deducted points
def update_taken_points(points):
    taken_points_data = load_data(TAKEN_POINTS_FILE)
    taken_points_data["total_taken_points"] = taken_points_data.get("total_taken_points", 0) + points
    save_data(TAKEN_POINTS_FILE, taken_points_data)

# Enable required intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Store last generated image for each user (expires in 10 seconds)
last_generated_image = {}
last_generated_time = {}
last_generated_prompt = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    global last_generated_image, last_generated_time, last_generated_prompt

    if message.author == client.user:
        return

    user_id = str(message.author.id)

    # Editing the last image (or regenerating it)
    if message.content.lower().startswith('!image now'):
        if user_id in last_generated_prompt:
            modification = message.content[len('!image now '):].strip()

            if not modification:
                await message.channel.send(f"🔄 Regenerating last image with prompt: **{last_generated_prompt[user_id]}**")
                new_image = await generate_image(last_generated_prompt[user_id])
                last_generated_image[user_id] = new_image
                last_generated_time[user_id] = time.time()

                image_file = discord.File(io.BytesIO(new_image), filename="generated_image.png")
                await message.channel.send(file=image_file)

                await asyncio.sleep(240)
                if time.time() - last_generated_time[user_id] >= 10:
                    last_generated_image.pop(user_id, None)
                    last_generated_time.pop(user_id, None)
            else:
                new_prompt = last_generated_prompt[user_id] + " " + modification
                await message.channel.send(f"🔄 Modifying last image with new prompt: {new_prompt}")

                new_image = await generate_image(new_prompt)

                if new_image:
                    last_generated_image[user_id] = new_image
                    last_generated_time[user_id] = time.time()
                    last_generated_prompt[user_id] = new_prompt

                    image_file = discord.File(io.BytesIO(new_image), filename="generated_image.png")
                    await message.channel.send(file=image_file)
                else:
                    await message.channel.send("⚠️ Failed to modify image. Please try again.")

                await asyncio.sleep(10)
                if time.time() - last_generated_time[user_id] >= 10:
                    last_generated_image.pop(user_id, None)
                    last_generated_time.pop(user_id, None)
                    last_generated_prompt.pop(user_id, None)
        else:
            await message.channel.send("❌ No recent image to edit or regenerate. Generate a new one first.")
        return

    # Generating a new image
    if message.content.lower().startswith('!image '):
        required_points = 1000
        current_points = get_user_points(user_id)

        if current_points < required_points:
            await message.channel.send("❌ You don't have enough points to generate an image.")
            return

        new_balance = current_points - required_points
        update_user_points(user_id, new_balance)
        update_taken_points(required_points)

        prompt = message.content[len('!image '):].strip()
        await message.channel.send(f"✅ 1000 points deducted. Remaining balance: **{new_balance}** points.\nGenerating image for: **{prompt}** ...")

        try:
            generated_image = await generate_image(prompt)

            if generated_image:
                last_generated_image[user_id] = generated_image
                last_generated_time[user_id] = time.time()
                last_generated_prompt[user_id] = prompt

                image_file = discord.File(io.BytesIO(generated_image), filename="generated_image.png")
                await message.channel.send(file=image_file)

                await asyncio.sleep(10)
                if time.time() - last_generated_time[user_id] >= 10:
                    last_generated_image.pop(user_id, None)
                    last_generated_time.pop(user_id, None)
                    last_generated_prompt.pop(user_id, None)
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("⚠️ An error occurred while processing your request.")

async def generate_image(prompt):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://image.pollinations.ai/prompt/{aiohttp.helpers.quote(prompt)}"
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    if image_data:
                        return image_data
                    else:
                        print(f"Error: No image data returned for prompt: {prompt}")
                        return None
                else:
                    print(f"Error: Failed to fetch image. Status: {response.status} for prompt: {prompt}")
                    return None
        except Exception as e:
            print(f"Error in generate_image: {e}")
            return None

# Start the bot
client.run(TOKEN)
