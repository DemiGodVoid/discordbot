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
players = []
uno_hands = {}
deck = [f"{color} {value}" for color in ["Red", "Green", "Blue", "Yellow"] for value in range(1, 10)] * 2
random.shuffle(deck)
current_card = None
turn_index = 0
points_in_pot = 0

def reset_game():
    global players, uno_hands, current_card, turn_index, points_in_pot
    players.clear()
    uno_hands.clear()
    current_card = None
    turn_index = 0
    points_in_pot = 0

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def start_uno(ctx):
    reset_game()
    await ctx.send("Game mode set to 2 players! Use `.join` to enter.")

@bot.command()
async def join(ctx):
    if len(players) < 2:
        players.append(ctx.author)
        await ctx.send(f"{ctx.author.name} has joined!")
    if len(players) == 2:
        await ask_for_bets(ctx)

async def ask_for_bets(ctx):
    global points_in_pot
    for player in players:
        await ctx.send(f"{player.mention}, enter the amount of points to bet:")
        def check(msg): return msg.author == player and msg.content.isdigit()
        bet_msg = await bot.wait_for("message", check=check)
        bet_amount = int(bet_msg.content)
        if points.get(str(player.id), 0) < bet_amount:
            await ctx.send("You don't got that many points yet!")
            return
        points[str(player.id)] -= bet_amount
        points_in_pot += bet_amount
    save_points()
    await ctx.send(f"Total points betted: {points_in_pot}")
    await start_game(ctx)

async def start_game(ctx):
    global current_card, turn_index
    await ctx.send("Dealing cards...")
    for player in players:
        uno_hands[player] = [deck.pop() for _ in range(7)]
    current_card = deck.pop()
    turn_index = 0
    await send_hands()
    await ctx.send(f"The starting card is **{current_card}**! {players[turn_index].mention}, it's your turn!")

async def send_hands():
    for player in players:
        embed = discord.Embed(title="Your Uno Hand", description="\n".join(uno_hands[player]), color=discord.Color.blue())
        await player.send(embed=embed)

@bot.command()
async def draw(ctx):
    player = players[turn_index]
    if ctx.author != player:
        return
    new_card = deck.pop()
    uno_hands[player].append(new_card)
    await send_hands()
    await ctx.send(f"{player.mention}, you drew **{new_card}**!")

@bot.event
async def on_message(message):
    global current_card, turn_index
    if message.author == bot.user:
        return
    
    if message.content.startswith("."):
        await bot.process_commands(message)
        return
    
    if message.author in players:
        player = players[turn_index]
        if message.author != player:
            return

        valid_moves = [card for card in uno_hands[player] if card.startswith(current_card.split()[0]) or card.endswith(current_card.split()[1])]
        content = message.content.lstrip(".")  # Ensure players must use "." before playing a card
        
        if content in uno_hands[player]:
            if content in valid_moves:
                current_card = content
                uno_hands[player].remove(content)
                await message.channel.send(f"{message.author.mention} played **{current_card}**!")
                if not uno_hands[player]:
                    await handle_win(message.author, message.channel)
                    return
            else:
                await bot.get_command("draw").invoke(await bot.get_context(message))
                return
            
            turn_index = (turn_index + 1) % 2
            await send_hands()
            await message.channel.send(f"{players[turn_index].mention}, it's your turn!")
        else:
            await message.channel.send("You don't have that card in your hand!")

async def handle_win(winner, channel):
    global points_in_pot
    points[str(winner.id)] = points.get(str(winner.id), 0) + points_in_pot
    save_points()
    await channel.send(f"{winner.mention} wins the game and takes {points_in_pot} points!")
    reset_game()

bot.run(token)
