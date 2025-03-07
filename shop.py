import discord
from discord.ext import commands

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True  # This enables the bot to read messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Event to indicate the bot is ready
@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')

# Command for !shop
@bot.command()
async def shop(ctx):
    # Create the embed message
    embed = discord.Embed(
        title="Shop",
        description="Here are the available actions:",
        color=discord.Color.blue()
    )

    # Add the !create_role text to the embed
    embed.add_field(name="!create_role", value="Cost: 5k points!", inline=False)
    embed.add_field(name="!group_name", value="Cost: 5k points!", inline=False)
    embed.add_field(name="!group_photo", value="Cost: 5k points!", inline=False)
    
    # Send the embed message to the channel
    await ctx.send(embed=embed)

# Load the bot token from token.txt
def get_bot_token():
    with open("token.txt", "r") as file:
        return file.read().strip()

# Run the bot
bot.run(get_bot_token())
