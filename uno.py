import discord
import json
import os
import random

from discord.ext import commands

# Check for token
if not os.path.exists("token.txt"):
    token = input("Enter your bot token: ")
    with open("token.txt", "w") as f:
        f.write(token)
else:
    with open("token.txt", "r") as f:
        token = f.read().strip()

# Load points
if not os.path.exists("points.json"):
    with open("points.json", "w") as f:
        json.dump({}, f)

with open("points.json", "r") as f:
    points = json.load(f)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True  # Ensure bot can read message content

bot = commands.Bot(command_prefix="!", intents=intents)
players = {}
uno_hands = {}
deck = [f"{color} {value}" for color in ["Red", "Green", "Blue", "Yellow"] for value in range(1, 10)] * 2
random.shuffle(deck)

def save_points():
    with open("points.json", "w") as f:
        json.dump(points, f)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def one(ctx):
    if "player1" not in players:
        players["player1"] = ctx.author
        await ctx.send("Player 1 has joined!")
    else:
        await ctx.send("Player 1 slot is taken!")

@bot.command()
async def two(ctx):
    if "player2" not in players:
        players["player2"] = ctx.author
        await ctx.send("Player 2 has joined!")
    else:
        await ctx.send("Player 2 slot is taken!")

@bot.command()
async def start_uno(ctx):
    if "player1" in players and "player2" in players:
        await ctx.send("Great! Before we start, let's throw in a few points.")
        await ctx.send(f"{players['player1'].mention}, enter an amount of points:")

        def check_p1(m):
            return m.author == players["player1"] and m.content.isdigit()
        
        msg1 = await bot.wait_for("message", check=check_p1)
        p1_points = int(msg1.content)
        points[str(players["player1"].id)] = points.get(str(players["player1"].id), 100) - p1_points
        
        await ctx.send(f"{players['player2'].mention}, enter an amount of points:")
        
        def check_p2(m):
            return m.author == players["player2"] and m.content.isdigit()
        
        msg2 = await bot.wait_for("message", check=check_p2)
        p2_points = int(msg2.content)
        points[str(players["player2"].id)] = points.get(str(players["player2"].id), 100) - p2_points
        
        total = p1_points + p2_points
        save_points()
        
        await ctx.send(f"Okay, player 1 put in {p1_points} and player 2 put in {p2_points}, which adds up to {total}! Whoever wins, takes this home!")
        
        uno_hands["player1"] = [deck.pop() for _ in range(7)]
        uno_hands["player2"] = [deck.pop() for _ in range(7)]
        
        await show_hands(ctx)
    else:
        await ctx.send("Both players need to join first by using !one and !two.")

async def show_hands(ctx):
    embed1 = discord.Embed(title=f"{players['player1'].name}'s Hand", description="\n".join(uno_hands["player1"]), color=discord.Color.red())
    embed2 = discord.Embed(title=f"{players['player2'].name}'s Hand", description="\n".join(uno_hands["player2"]), color=discord.Color.blue())
    
    await players["player1"].send(embed=embed1)
    await players["player2"].send(embed=embed2)
    await ctx.send("Both players have received their starting hands! Let the game begin!")

bot.run(token)
