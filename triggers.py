import discord
from discord.ext import commands
import json
import os

# Load triggers from file
def load_triggers():
    if os.path.exists("triggers.json"):
        with open("triggers.json", "r") as f:
            return json.load(f)
    return {}

# Save triggers to file
def save_triggers(triggers):
    with open("triggers.json", "w") as f:
        json.dump(triggers, f, indent=4)

# Load bot token from file
def load_token():
    with open("token.txt", "r") as f:
        return f.read().strip()

# Initialize bot
intents = discord.Intents.all()  # Enable all intents

bot = commands.Bot(command_prefix="!", intents=intents)
triggers = load_triggers()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def trigger(ctx, *, arg):
    """Command to add a trigger."""
    if "=" not in arg:
        await ctx.send("Invalid format! Use: !trigger TRIGGER=RESPONSE")
        return
    
    trigger, response = arg.split("=", 1)
    guild_id = str(ctx.guild.id)
    
    if guild_id not in triggers:
        triggers[guild_id] = {}
    
    triggers[guild_id][trigger.strip()] = response.strip()
    save_triggers(triggers)
    await ctx.send(f'Trigger "{trigger.strip()}" added!')

@bot.command()
async def list(ctx):
    """Command to list all triggers."""
    guild_id = str(ctx.guild.id)
    if guild_id in triggers and triggers[guild_id]:
        await ctx.send("Triggers: " + ", ".join(triggers[guild_id].keys()))
    else:
        await ctx.send("No triggers set!")

@bot.command()
async def delete(ctx, *, trigger):
    """Command to delete a trigger."""
    guild_id = str(ctx.guild.id)
    
    if guild_id in triggers and trigger.strip() in triggers[guild_id]:
        del triggers[guild_id][trigger.strip()]
        save_triggers(triggers)
        await ctx.send(f'Trigger "{trigger.strip()}" deleted!')
    else:
        await ctx.send(f'Trigger "{trigger.strip()}" not found!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)  # Ensure commands are processed

    guild_id = str(message.guild.id)
    if guild_id in triggers:
        for trigger, response in triggers[guild_id].items():
            if trigger.lower() in message.content.lower():  # Case-insensitive check
                await message.channel.send(response)
                break

# Run the bot
TOKEN = load_token()
bot.run(TOKEN)
