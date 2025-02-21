import discord
from discord.ext import commands
import yt_dlp
import asyncio
import audioread
import io

intents = discord.Intents.default()
intents.voice_states = True  # Allow tracking voice state updates
intents.guilds = True  # Ensure the bot can access guild (server) info
intents.message_content = True  # Allow bot to read message content (required for commands)

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
async def join(ctx):
    # Ensure the user is in a voice channel
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("You must be in a voice channel to use this command!")
        return

    voice_channel = ctx.author.voice.channel
    
    try:
        # If the bot is already connected, move it to the user’s voice channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(voice_channel)
        else:
            # Connect the bot to the user's current voice channel
            vc = await voice_channel.connect()
            await ctx.send(f"Connected to {voice_channel}")
            print(f"Bot connected to {voice_channel}")
    except Exception as e:
        print(f"Error connecting to voice channel: {e}")
        await ctx.send("I couldn't join the voice channel. Please check my permissions and try again.")

@bot.command()
async def que(ctx, url: str):
    # Ensure the user is in a voice channel
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("You must be in a voice channel to use this command!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    try:
        # If the bot is already connected, move it to the user’s voice channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(voice_channel)
        else:
            vc = await voice_channel.connect()
            print(f"Bot connected to {voice_channel}")
    except Exception as e:
        print(f"Error connecting to voice channel: {e}")
        await ctx.send("I couldn't join the voice channel. Please check my permissions and try again.")
        return
    
    vc = ctx.voice_client
    
    ydl_opts = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
    except Exception as e:
        print(f"Error extracting audio: {e}")
        await ctx.send("There was an error fetching the audio from the provided URL.")
        return
    
    # Use audioread to decode and stream the audio
    with audioread.audio_open(url2) as f:
        # Create an audio stream from the downloaded file
        pcm_data = io.BytesIO(f.read())  # Read the audio into memory
    
    # Now, stream the audio using FFmpegPCMAudio
    vc.play(discord.FFmpegPCMAudio(pcm_data), after=lambda e: print(f'Finished playing: {e}'))
    
    await ctx.send(f'Now playing: {info["title"]}')
    
    # Wait until audio is finished before disconnecting
    while vc.is_playing():
        await asyncio.sleep(1)
    
    await vc.disconnect()

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and not before.channel and after.channel in [vc.channel for vc in bot.voice_clients]:
        await member.edit(mute=True)  # Mute anyone who joins

bot.run(get_token())
