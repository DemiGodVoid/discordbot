import discord
import json
import os
import aiohttp

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required to detect member joins
client = discord.Client(intents=intents)

# Load or request bot token
TOKEN_FILE = "token.txt"

if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()
else:
    TOKEN = input("Please enter your Discord bot token: ").strip()
    with open(TOKEN_FILE, "w") as f:
        f.write(TOKEN)

# File paths
TRIGGERS_FILE = "triggers.json"
RULES_FILE = "rules.json"

# Load data functions
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Load triggers and rules
triggers = load_data(TRIGGERS_FILE)
rules = load_data(RULES_FILE)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_member_join(member):
    """Send rules in the channel where the member joined."""
    guild_id = str(member.guild.id)

    if guild_id in rules and rules[guild_id]:
        rule_message = f"Welcome to **{member.guild.name}**, {member.mention}!\n\n**Server Rules:**\n{rules[guild_id]}"

        # Find the first available text channel where the bot can send messages
        for channel in member.guild.text_channels:
            if channel.permissions_for(member.guild.me).send_messages:
                await channel.send(rule_message)
                break

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    guild_id = str(message.guild.id)

    if guild_id not in triggers:
        triggers[guild_id] = {}
    if guild_id not in rules:
        rules[guild_id] = {}

    msg_lower = message.content.lower()

    if msg_lower in triggers[guild_id]:
        await message.channel.send(triggers[guild_id][msg_lower])

    if message.content == '!ping':
        await message.channel.send('PONG')

    if message.content == '!commands':
        await message.channel.send(
            'Commands:\n\n!ping\n\n!gif message (send a related GIF)\n\n'
            '!trigger message=message (set a trigger response)\n\n'
            '!set_rules message (set server rules)\n\n!rules (view server rules)\n\n!commands2 (More commands)'
        )

    # 🔥 Updated !gif command: Sends only the GIF, no extra text
    if message.content.startswith("!gif "):
        search_term = message.content[len("!gif "):].strip().replace(" ", "+")
        tenor_api_url = f"https://g.tenor.com/v1/search?q={search_term}&key=LIVDSRZULELA&limit=1"

        async with aiohttp.ClientSession() as session:
            async with session.get(tenor_api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "results" in data and len(data["results"]) > 0:
                        gif_url = data["results"][0]["media"][0]["gif"]["url"]
                        await message.channel.send(gif_url)  # Sends only the GIF (auto-embeds)
                        return

        await message.channel.send("Couldn't find a GIF for that.")

    if message.content.startswith("!trigger "):
        parts = message.content[len("!trigger "):].split("=")
        if len(parts) == 2:
            trigger, response = parts[0].strip().lower(), parts[1].strip()
            triggers[guild_id][trigger] = response
            save_data(TRIGGERS_FILE, triggers)
            await message.channel.send(f"Trigger set: '{trigger}' → '{response}'")
        else:
            await message.channel.send("Invalid format. Use: `!trigger message=message`")

    if message.content.startswith("!set_rules "):
        rules_text = message.content[len("!set_rules "):].strip()
        if rules_text:
            rules[guild_id] = rules_text
            save_data(RULES_FILE, rules)
            await message.channel.send(f"Server rules set:\n{rules_text}")
        else:
            await message.channel.send("Please provide the rules after the command. Usage: `!set_rules <rules>`")

    if message.content == "!rules":
        if guild_id in rules and rules[guild_id]:
            await message.channel.send(f"Server Rules:\n\n{rules[guild_id]}")
        else:
            await message.channel.send("No rules have been set for this server yet.")

client.run(TOKEN)
