import discord
import json
import os
import googleapiclient.discovery

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

# Load or request bot token
TOKEN_FILE = "token.txt"
YOUTUBE_API_FILE = "youtube_api.txt"

if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()
else:
    TOKEN = input("Please enter your Discord bot token: ").strip()
    with open(TOKEN_FILE, "w") as f:
        f.write(TOKEN)

# Load or request YouTube API key
if os.path.exists(YOUTUBE_API_FILE):
    with open(YOUTUBE_API_FILE, "r") as f:
        YOUTUBE_API_KEY = f.read().strip()
else:
    YOUTUBE_API_KEY = input("Please enter your YouTube API key: ").strip()
    with open(YOUTUBE_API_FILE, "w") as f:
        f.write(YOUTUBE_API_KEY)

# File paths
RULES_FILE = "rules.json"
POINTS_FILE = "points.json"
TAKEN_POINTS_FILE = "taken_points.json"

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

rules = load_data(RULES_FILE)
points_data = load_data(POINTS_FILE)
taken_points = load_data(TAKEN_POINTS_FILE)

def search_youtube(query):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=query, part="snippet", type="video", maxResults=1)
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        video_id = response["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
    return "No results found."

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
@client.event
async def on_member_join(member):
    """ Sends the rules when a new member joins """
    guild_id = str(member.guild.id)

    if guild_id in rules and rules[guild_id]:
        rule_text = f"**Welcome {member.mention}!**\n\n**Server Rules:**\n{rules[guild_id]}"
    else:
        rule_text = f"**Welcome {member.mention}!**\nNo rules have been set for this server."

    # Try to send to the system channel (usually the welcome channel)
    if member.guild.system_channel and member.guild.system_channel.permissions_for(member.guild.me).send_messages:
        await member.guild.system_channel.send(rule_text)
    else:
        # Otherwise, find the first available text channel where the bot has permission
        for channel in member.guild.text_channels:
            if channel.permissions_for(member.guild.me).send_messages:
                await channel.send(rule_text)
                break

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    guild_id = str(message.guild.id)

    if message.content == '!rules':
        if guild_id in rules and rules[guild_id]:
            await message.channel.send(f"**Server Rules:**\n{rules[guild_id]}")
        else:
            await message.channel.send("No rules have been set for this server.")

    if message.content.startswith('!set_rules '):
        if message.author.guild_permissions.administrator:
            new_rules = message.content[len('!set_rules '):].strip()
            rules[guild_id] = new_rules
            save_data(RULES_FILE, rules)
            await message.channel.send("Server rules updated successfully!")
        else:
            await message.channel.send("You do not have permission to set rules.")

    if message.content == '!commands':
        embed = discord.Embed(title="Baisc Server Commands", description="List of available commands", color=discord.Color.blue())
        embed.add_field(name="!rules", value="View server Rules", inline=False)
        embed.add_field(name="!roles", value="Let users pick thier own roles.(Hides Admin roles/Owner roles and bot roles.)", inline=False)
        embed.add_field(name="!set_rules", value="Set server Rules (Admin only)", inline=False)
        embed.add_field(name="!games", value="List available games", inline=False)
        embed.add_field(name="!funcommands", value="View Fun commands", inline=False)
        await message.channel.send(embed=embed)

    if message.content == '!funcommands':
        embed = discord.Embed(title="Fun Commands", description="Additional fun and utility commands", color=discord.Color.blue())
        embed.add_field(name="!youtube title - name", value="Search for a YouTube video.", inline=False)
        embed.add_field(name="!shop", value="View the bots shop!", inline=False)
        embed.add_field(name="!search prompt", value="Use the bots search engine! cost 500 points", inline=False)
        embed.add_field(name="!chat prompt", value="Chat with the bots gpt mindset! cost 500 points.", inline=False)
        embed.add_field(name="!image prompt", value="Make the bot generate an image! cost 1k points.", inline=False)
        embed.add_field(name="!confess", value="DM me !confess MESSAGE to anonymously confess to a server!", inline=False)
        embed.add_field(name="!reels_on", value="Make me send reels every 60 minutes!", inline=False)
        await message.channel.send(embed=embed)

    if message.content == '!games':
        embed = discord.Embed(title="Bot Games", description="List of available games", color=discord.Color.green())
        embed.add_field(name="!connect4", value="Play Connect 4! Win points", inline=False)
        embed.add_field(name="!blackjack", value="Play blackjack and bet your points.", inline=False)
        embed.add_field(name=".start_uno", value="Play uno!(Cast your bets and win!).", inline=False)
        embed.add_field(name=".wheel", value="Spin the wheel and win the jackpot(takes 500 points).", inline=False)
        embed.add_field(name="!roll amount", value="Gamble points.", inline=False)
        embed.add_field(name="!bal", value="Check your points.", inline=False)
        embed.add_field(name="!points", value="See all points.", inline=False)
        embed.add_field(name="!taken", value="Total spent points.", inline=False)
        await message.channel.send(embed=embed)

    if message.content.startswith('!youtube '):
        query = message.content[len('!youtube '):].strip()
        video_url = search_youtube(query)
        await message.channel.send(f"YouTube Search Result: {video_url}")

client.run(TOKEN)
