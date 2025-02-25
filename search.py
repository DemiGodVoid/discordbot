import discord
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from discord.ext import commands

# Read bot token from token.txt
with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to scrape DuckDuckGo search results
def search_web(query):
    url = f"https://duckduckgo.com/html/?q={query}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.select(".result__title a")[:3]:  # Get top 3 results
        title = result.get_text(strip=True)
        href = result["href"]

        # Extract real URL from DuckDuckGo redirection
        if "uddg=" in href:
            href = unquote(href.split("uddg=")[-1].split("&")[0])  # Decode URL

        results.append(f"[**{title}**]({href})")  # Clickable Discord embed format

    return results if results else None

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Command: !search <query>
@bot.command()
async def search(ctx, *, query: str = None):
    if not query:
        await ctx.send("❌ **Please provide a search term!**")
        return

    results = search_web(query)

    if results:
        response = "**🔎 Top Search Results:**\n\n" + "\n\n".join(results)
        await ctx.send(response)
    else:
        await ctx.send("❌ **No results found.**")

# Run the bot
bot.run(TOKEN)

