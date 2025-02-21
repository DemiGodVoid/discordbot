import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
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
async def que(ctx, url: str):
    # Download the audio as an MP3 file
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save to a temporary file
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = filename.rsplit('.', 1)[0] + '.mp3'  # Ensure the correct file extension
    except Exception as e:
        print(f"Error downloading audio: {e}")
        await ctx.send("There was an error fetching the audio from the provided URL.")
        return

    # Send the audio file to the text channel
    try:
        await ctx.send(f"Now playing: {info['title']}", file=discord.File(filename))
    except Exception as e:
        print(f"Error sending file: {e}")
        await ctx.send("There was an error sending the audio file.")
    
    # Clean up the downloaded file
    try:
        os.remove(filename)
    except:
        pass

@bot.command()
async def leave(ctx):
    await ctx.send("I don't need to leave since I'm not connected to a voice channel.")

bot.run(get_token())
