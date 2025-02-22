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

def save_points():
    with open("points.json", "w") as f:
        json.dump(points, f)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)
players = {}
uno_hands = {}
deck = [f"{color} {value}" for color in ["Red", "Green", "Blue", "Yellow"] for value in range(1, 10)] * 2
random.shuffle(deck)
current_card = None
points_in_pot = 0

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def start_uno(ctx):
    global current_card, points_in_pot
    players.clear()
    uno_hands.clear()
    points_in_pot = 0
    await ctx.send("Both players need to join! Use .one and .two to join the game.")

@bot.command()
async def one(ctx):
    if "player1" not in players:
        players["player1"] = ctx.author
        await ctx.send("Player 1 has joined!")
    else:
        await ctx.send("Player 1 slot is taken!")
    await check_start(ctx)

@bot.command()
async def two(ctx):
    if "player2" not in players:
        players["player2"] = ctx.author
        await ctx.send("Player 2 has joined!")
    else:
        await ctx.send("Player 2 slot is taken!")
    await check_start(ctx)

async def check_start(ctx):
    global current_card, points_in_pot
    if "player1" in players and "player2" in players:
        await ctx.send("Both players are ready! Enter your bet amount.")
        
        def check_p1(m):
            return m.author == players["player1"] and m.content.isdigit()
        
        await ctx.send(f"{players['player1'].mention}, enter your bet:")
        msg1 = await bot.wait_for("message", check=check_p1)
        p1_bet = int(msg1.content)
        points[str(players["player1"].id)] = points.get(str(players["player1"].id), 100) - p1_bet
        
        def check_p2(m):
            return m.author == players["player2"] and m.content.isdigit()
        
        await ctx.send(f"{players['player2'].mention}, enter your bet:")
        msg2 = await bot.wait_for("message", check=check_p2)
        p2_bet = int(msg2.content)
        points[str(players["player2"].id)] = points.get(str(players["player2"].id), 100) - p2_bet
        
        points_in_pot = p1_bet + p2_bet
        save_points()
        
        await ctx.send(f"Player 1 bet {p1_bet} and Player 2 bet {p2_bet}, total pot is {points_in_pot}!")
        
        await start_game(ctx)

async def start_game(ctx):
    global current_card
    await ctx.send("Dealing cards...")
    uno_hands["player1"] = [deck.pop() for _ in range(7)]
    uno_hands["player2"] = [deck.pop() for _ in range(7)]
    await send_hands()
    current_card = deck.pop()
    await ctx.send(f"The starting card is **{current_card}**!")
    await ctx.send(f"{players['player1'].mention}, it's your turn! Say your card to play.")

async def send_hands():
    embed1 = discord.Embed(title=f"Your Uno Hand", description="\n".join(uno_hands["player1"]), color=discord.Color.red())
    embed2 = discord.Embed(title=f"Your Uno Hand", description="\n".join(uno_hands["player2"]), color=discord.Color.blue())
    await players["player1"].send(embed=embed1)
    await players["player2"].send(embed=embed2)

@bot.event
async def on_message(message):
    global current_card
    if message.author == bot.user or not message.content.startswith("."):
        return
    
    content = message.content[1:].strip()
    if message.author in players.values():
        player = "player1" if message.author == players["player1"] else "player2"
        opponent = "player2" if player == "player1" else "player1"
        valid_moves = [card for card in uno_hands[player] if card.startswith(current_card.split()[0]) or card.endswith(current_card.split()[1])]
        
        if content in uno_hands[player]:
            if content in valid_moves:
                uno_hands[player].remove(content)
                current_card = content
                await message.channel.send(f"{message.author.mention} played **{current_card}**! Now it's {players[opponent].mention}'s turn.")
                await send_hands()
                
                if not uno_hands[player]:
                    points[str(players[player].id)] += points_in_pot
                    save_points()
                    await message.channel.send(f"{players[player].mention} wins the game and takes home {points_in_pot} points!")
                    return
            else:
                await message.channel.send("Invalid move! You must match the color or the number.")
        else:
            await message.channel.send("You don't have that card in your hand!")
    
    await bot.process_commands(message)

bot.run(token)
