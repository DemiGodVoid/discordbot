import discord
from discord.ext import commands
import os
import random
import json

TOKEN_FILE = "token.txt"
POINTS_FILE = "points.json"

if not os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "w") as f:
        f.write(input("Enter your bot token: "))

with open(TOKEN_FILE, "r") as f:
    TOKEN = f.read().strip()

# Load player points
def load_points():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r") as f:
            points_data = json.load(f)
            print(f"Loaded points: {points_data}")  # Debugging line to check loaded points
            return points_data
    return {}

def save_points(points):
    print(f"Saving points: {points}")  # Debugging line to check what points are being saved
    with open(POINTS_FILE, "w") as f:
        json.dump(points, f)

player_points = load_points()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Required for command processing

bot = commands.Bot(command_prefix="!", intents=intents)

game_active = False
players = []
turn = 0
board = [["⚪" for _ in range(7)] for _ in range(6)]
player_symbols = {}

async def display_board(ctx):
    board_str = "\n".join(" ".join(row) for row in board)
    column_numbers = "1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣"
    await ctx.send(f"```\n{board_str}\n```\n{column_numbers}")

def drop_piece(column, symbol):
    for row in reversed(board):
        if row[column] == "⚪":
            row[column] = symbol
            return True
    return False

def check_winner():
    for row in range(6):
        for col in range(7):
            if board[row][col] == "⚪":
                continue
            symbol = board[row][col]
            directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
            for dr, dc in directions:
                try:
                    if all(board[row + dr * i][col + dc * i] == symbol for i in range(4)):
                        return symbol
                except IndexError:
                    continue
    return None

@bot.command()
async def connect4(ctx):
    global game_active, players, board, turn, player_symbols
    if game_active:
        await ctx.send("A game is already in progress!")
        return
    game_active = True
    players = []
    board = [["⚪" for _ in range(7)] for _ in range(6)]
    await ctx.send("Connect 4 started! Type `!one` to join as Player 1 (🔴) and `!two` to join as Player 2 (🟡).")

@bot.command()
async def one(ctx):
    global players, player_symbols
    if len(players) >= 1:
        await ctx.send("Player 1 already taken! Waiting for Player 2.")
        return
    players.append(ctx.author)
    player_symbols[ctx.author] = "🔴"
    await ctx.send(f"{ctx.author.mention} joined as Player 1! Waiting for Player 2.")

@bot.command()
async def two(ctx):
    global game_active, turn
    if len(players) != 1:
        await ctx.send("Player 1 must join first with `!one`.")
        return
    if ctx.author in players:
        await ctx.send("You are already in the game!")
        return
    players.append(ctx.author)
    player_symbols[ctx.author] = "🟡"
    await ctx.send(f"{ctx.author.mention} joined as Player 2! All players found. Let's start!")
    await display_board(ctx)
    await ctx.send(f"{players[turn].mention}, it's your turn! Choose a column (1-7) by typing the number.")

@bot.command()
async def drop(ctx, column: int):
    await process_move(ctx, column)

async def process_move(ctx, column: int):
    global turn, game_active
    if not game_active or len(players) < 2:
        await ctx.send("The game isn't running! Use `!connect4` to start a game.")
        return
    if ctx.author != players[turn]:
        await ctx.send("It's not your turn!")
        return
    if column < 1 or column > 7:
        await ctx.send("Invalid column! Pick a number between 1-7.")
        return
    if not drop_piece(column - 1, player_symbols[ctx.author]):
        await ctx.send("Column full! Pick another.")
        return
    await display_board(ctx)
    winner = check_winner()
    if winner:
        await reward_winner(ctx, players[turn])
        game_active = False
        return
    turn = 1 - turn
    await ctx.send(f"{players[turn].mention}, it's your turn! Choose a column (1-7).")

async def reward_winner(ctx, winner):
    user_id = str(winner.id)
    reward_tier = random.choices(["low", "medium", "high"], [50, 35, 15])[0]
    if reward_tier == "low":
        points = random.randint(0, 100)
    elif reward_tier == "medium":
        points = random.randint(100, 250)
    else:
        points = random.randint(250, 500)

    if user_id not in player_points:
        player_points[user_id] = 0
    player_points[user_id] += points
    save_points(player_points)

    await ctx.send(f"{winner.mention} ({player_symbols[winner]}) wins! 🎉 You won {points} points!")

@bot.command()
async def points(ctx):
    sorted_points = sorted(player_points.items(), key=lambda x: x[1], reverse=True)
    leaderboard = "\n".join([f"<@{user_id}>: {points} points" for user_id, points in sorted_points])
    await ctx.send(f"**Leaderboard:**\n{leaderboard}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    ctx = await bot.get_context(message)

    if game_active and len(players) == 2 and message.author in players:
        try:
            column = int(message.content.strip())
            if 1 <= column <= 7:
                await process_move(ctx, column)
                return
        except ValueError:
            pass

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
