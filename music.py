import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import asyncio
import os

# --- Load Secrets ---
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()


SPOTIFY_CLIENT_ID = "d873617066364d3cb4d39ba2b5cc37ea"
SPOTIFY_CLIENT_SECRET = "159da76350fa4bc6b01a7eff8cbc77a6"

VOICE_CHANNEL_ID = 1355261126023053492  # Replace with your voice channel ID
TEXT_CHANNEL_ID = 1340536425405223064  # Replace with your text channel ID

# Spotify Setup
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = asyncio.Queue()
is_playing = False

async def play_next(vc):
    global is_playing
    if queue.empty():
        is_playing = False
        return

    song_url = await queue.get()
    is_playing = True
    ffmpeg_options = {"options": "-vn"}
    vc.play(discord.FFmpegPCMAudio(song_url, **ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(vc), bot.loop))

@bot.command()
async def music(ctx, *, song_name: str):
    global is_playing
    if ctx.channel.id != TEXT_CHANNEL_ID:
        return

    try:
        # Search on Spotify
        results = sp.search(q=song_name, limit=1, type="track")
        if not results['tracks']['items']:
            await ctx.send("Song not found on Spotify.")
            return

        track = results['tracks']['items'][0]
        song_title = f"{track['name']} {track['artists'][0]['name']}"

        # Search on YouTube
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_title}", download=False)
            song_url = info['entries'][0]['url']

        # Join voice channel
        vc = ctx.guild.voice_client
        if not vc:
            channel = ctx.guild.get_channel(VOICE_CHANNEL_ID)
            vc = await channel.connect()
        
        # Mute everyone
        for member in vc.channel.members:
            if not member.bot:
                await member.edit(mute=True)

        # Queue song or play immediately
        await queue.put(song_url)
        if not is_playing:
            await play_next(vc)
        
        await ctx.send(f"Added to queue: {song_title}")

    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def skip(ctx):
    """Skips the current song and plays the next one in the queue."""
    vc = ctx.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("Skipped song.")
    else:
        await ctx.send("No song is currently playing.")

@bot.event
async def on_voice_state_update(member, before, after):
    """Mute users when they join the music channel."""
    if after.channel and after.channel.id == VOICE_CHANNEL_ID and not member.bot:
        await member.edit(mute=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
