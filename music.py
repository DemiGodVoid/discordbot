import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.voice_states = True  # Allow tracking voice state updates

bot = commands.Bot(command_prefix='!', intents=intents)

def get_token():
    try:
        with open("token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return input("Enter your bot token: ")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def que(ctx, url: str):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("You must be in a voice channel to use this command!")
        return
    
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()
    
    ydl_opts = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
    
    vc.play(discord.FFmpegPCMAudio(url2), after=lambda e: print(f'Finished playing: {e}'))
    
    await ctx.send(f'Now playing: {info["title"]}')
    
    while vc.is_playing():
        await asyncio.sleep(1)
    
    await vc.disconnect()

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and not before.channel and after.channel in [vc.channel for vc in bot.voice_clients]:
        await member.edit(mute=True)  # Mute anyone who joins

bot.run(get_token())
