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
deck += ["+4"] * 4  # Adding +4 cards
random.shuffle(deck)
current_card = None
points_in_pot = 0
turn_index = 0
game_mode = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def start_uno(ctx):
    global game_mode
    players.clear()
    uno_hands.clear()
    game_mode = None
    await ctx.send("Choose a game mode: `.2 players` or `.4 players`.")

@bot.command()
async def two_players(ctx):
    global game_mode
    if game_mode is None:
        game_mode = 2
        await ctx.send("Game mode set to 2 players! Use `.one` and `.two` to join.")

@bot.command()
async def four_players(ctx):
    global game_mode
    if game_mode is None:
        game_mode = 4
        await ctx.send("Game mode set to 4 players! Use `.one`, `.two`, `.three`, and `.four` to join.")

@bot.command()
async def one(ctx):
    await add_player(ctx, ctx.author)

@bot.command()
async def two(ctx):
    await add_player(ctx, ctx.author)

@bot.command()
async def three(ctx):
    if game_mode == 4:
        await add_player(ctx, ctx.author)

@bot.command()
async def four(ctx):
    if game_mode == 4:
        await add_player(ctx, ctx.author)

async def add_player(ctx, player):
    if player not in players and len(players) < game_mode:
        players.append(player)
        await ctx.send(f"{player.name} has joined!")
    if len(players) == game_mode:
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

@bot.event
async def on_message(message):
    global current_card, turn_index, game_mode
    if message.author == bot.user:
        return
    
    content = message.content.strip()
    if content == ".2 players":
        await two_players(await bot.get_context(message))
        return
    elif content == ".4 players":
        await four_players(await bot.get_context(message))
        return
    
    if message.content.startswith("."):
        await bot.process_commands(message)
        return
    
    if message.author in players:
        player = players[turn_index]
        if message.author != player:
            return  # Ignore messages from non-turn players

        valid_moves = [card for card in uno_hands[player] if card.startswith(current_card.split()[0]) or card.endswith(current_card.split()[1]) or card == "+4"]
        
        if content in uno_hands[player]:
            if content == "+4":
                next_player = players[(turn_index + 1) % game_mode]
                uno_hands[next_player].extend([deck.pop() for _ in range(4)])
                await message.channel.send(f"{message.author.mention} played **+4**! {next_player.mention} draws 4 cards!")
            elif content in valid_moves:
                current_card = content
                uno_hands[player].remove(content)
                await message.channel.send(f"{message.author.mention} played **{current_card}**!")
                
                if not uno_hands[player]:
                    await message.channel.send(f"{message.author.mention} wins the game!")
                    return
            else:
                await message.channel.send("Invalid move! You must match the color or the number, or play +4.")
                return
            
            turn_index = (turn_index + 1) % game_mode
            await send_hands()
            await message.channel.send(f"{players[turn_index].mention}, it's your turn!")
        else:
            await message.channel.send("You don't have that card in your hand!")

bot.run(token)
