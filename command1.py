import discord
import random
import asyncio
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable member intents to fetch server members
client = discord.Client(intents=intents)

TOKEN = input("Please enter your Discord bot token: ")

# File paths for storing persistent data
TRIGGERS_FILE = "triggers.json"
RULES_FILE = "rules.json"
MEMES_FILE = "memes.txt"

# Function to load JSON data
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

# Function to save JSON data
def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Function to load meme templates from memes.txt
def load_memes():
    if os.path.exists(MEMES_FILE):
        with open(MEMES_FILE, "r") as f:
            return f.readlines()
    return []

# Load persistent data
triggers = load_data(TRIGGERS_FILE)  # Triggers per server
rules = load_data(RULES_FILE)  # Rules per server
meme_templates = load_memes()  # Meme templates from memes.txt

# Background task variables
meme_task = None
meme_interval = None

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_member_join(member):
    """Sends rules to new members when they join."""
    guild_id = str(member.guild.id)
    if guild_id in rules:
        await member.send(f"Welcome to the server! Here are the server rules:\n\n{rules[guild_id]}")
    else:
        await member.send("Welcome to the server! No rules have been set yet.")

async def send_meme_periodically(channel, interval):
    """Sends a meme periodically to the specified channel."""
    global meme_task
    while meme_task is not None:  # Ensure the task runs until explicitly stopped
        members = [member for member in channel.guild.members if not member.bot]
        if len(members) < 2:
            await channel.send("Not enough members to generate a meme!")
            return

        # Pick two random members
        user1, user2 = random.sample(members, 2)
        user1_mention = user1.mention
        user2_mention = user2.mention

        # Pick a random meme template
        meme = random.choice(meme_templates).strip().format(user1=user1_mention, user2=user2_mention)
        await channel.send(meme)

        # Wait for the specified interval before sending the next meme
        await asyncio.sleep(interval * 60)

@client.event
async def on_message(message):
    global meme_task, meme_interval, triggers, rules

    if message.author == client.user:
        return

    # Get server (guild) ID to store data per server
    guild_id = str(message.guild.id)

    # Ensure the guild has an entry in triggers and rules
    if guild_id not in triggers:
        triggers[guild_id] = {}
    if guild_id not in rules:
        rules[guild_id] = {}

    # Convert message to lowercase for case-insensitive checks
    msg_lower = message.content.lower()

    # Respond to a trigger message if it exists
    if msg_lower in triggers[guild_id]:
        await message.channel.send(triggers[guild_id][msg_lower])

    # Ping command
    if message.content == '!ping':
        await message.channel.send('PONG')

    # Commands list
    if message.content == '!commands':
        await message.channel.send(
            'Commands:\n\n!ping\n\n!meme\n\n!meme number (auto-send memes every X minutes)\n\n'
            '!stopmeme\n\n!trigger message=message (set a trigger response)\n\n!set_rules message (set server rules)\n'
        )

    # Meme command
    if message.content.startswith('!meme'):
        if message.content == '!meme':  # Single meme command
            members = [member for member in message.guild.members if not member.bot]
            if len(members) < 2:
                await message.channel.send("Not enough members to generate a meme!")
                return

            # Pick two random members
            user1, user2 = random.sample(members, 2)
            user1_mention = user1.mention
            user2_mention = user2.mention

            # Pick a random meme template
            meme = random.choice(meme_templates).strip().format(user1=user1_mention, user2=user2_mention)
            await message.channel.send(meme)

        elif message.content.startswith('!meme '):  # Auto-meme command
            try:
                interval = int(message.content.split(' ')[1])
                if interval < 1:
                    await message.channel.send("Please enter a number greater than 0.")
                    return

                meme_interval = interval
                if meme_task is not None:
                    meme_task.cancel()  # Cancel any existing auto-meme task
                meme_task = asyncio.create_task(send_meme_periodically(message.channel, meme_interval))
                await message.channel.send(f"Auto-memes enabled. A meme will be sent every {meme_interval} minute(s).")

            except ValueError:
                await message.channel.send("Invalid format. Use: !meme number")

    # Stop auto-meme command
    if message.content == '!stopmeme':
        if meme_task is not None:
            meme_task.cancel()
            meme_task = None
            await message.channel.send("Auto-memes disabled.")
        else:
            await message.channel.send("Auto-memes are not currently running.")

    # Trigger message command (store persistently)
    if message.content.startswith("!trigger "):
        parts = message.content[len("!trigger "):].split("=")
        if len(parts) == 2:
            trigger, response = parts[0].strip().lower(), parts[1].strip()
            triggers[guild_id][trigger] = response
            save_data(TRIGGERS_FILE, triggers)  # Save persistently
            await message.channel.send(f"Trigger set: '{trigger}' → '{response}'")
        else:
            await message.channel.send("Invalid format. Use: `!trigger message=message`")

    # Set rules command (store persistently)
    if message.content.startswith("!set_rules "):
        rules_text = message.content[len("!set_rules "):].strip()
        if rules_text:
            rules[guild_id] = rules_text
            save_data(RULES_FILE, rules)  # Save persistently
            await message.channel.send(f"Server rules set:\n{rules_text}")
        else:
            await message.channel.send("Please provide the rules after the command. Usage: `!set_rules <rules>`")

client.run(TOKEN)
