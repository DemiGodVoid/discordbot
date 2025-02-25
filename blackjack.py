import discord
from discord.ext import commands
import random
import json

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

points_file = 'points.json'
taken_points_file = 'taken_points.json'
active_games = {}
deck = []

def load_points():
    try:
        with open(points_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_points(points):
    with open(points_file, 'w') as f:
        json.dump(points, f)

def load_taken_points():
    try:
        with open(taken_points_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"total_taken_points": 0}

def save_taken_points(taken_points):
    with open(taken_points_file, 'w') as f:
        json.dump(taken_points, f)

def shuffle_deck():
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    deck = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def deal_hand(deck):
    return [deck.pop(), deck.pop()]

def hand_value(hand):
    value, num_aces = 0, 0
    for card in hand:
        if card['rank'] in ['Jack', 'Queen', 'King']:
            value += 10
        elif card['rank'] == 'Ace':
            value += 11
            num_aces += 1
        else:
            value += int(card['rank'])
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def blackjack(ctx):
    if ctx.author.id in active_games:
        await ctx.send("You already have a game in progress! Use `!hit` or `!stand`.")
        return
    active_games[ctx.author.id] = {"bet": 0, "deck": shuffle_deck(), "player_hand": [], "dealer_hand": []}
    await ctx.send(f"{ctx.author.mention}, enter your bet amount using `!bet <amount>`")

@bot.command()
async def bet(ctx, amount: int):
    if amount <= 0:
        await ctx.send(f"{ctx.author.mention}, you must bet a positive amount!")
        return
    if ctx.author.id not in active_games:
        await ctx.send("Start a game first with `!blackjack`.")
        return
    points = load_points()
    if str(ctx.author.id) not in points or points[str(ctx.author.id)] < amount:
        await ctx.send(f"{ctx.author.mention}, you don't have enough points!")
        del active_games[ctx.author.id]
        return
    points[str(ctx.author.id)] -= amount
    save_points(points)
    game = active_games[ctx.author.id]
    game["bet"] = amount
    game["player_hand"] = deal_hand(game["deck"])
    game["dealer_hand"] = deal_hand(game["deck"])
    await ctx.send(f"{ctx.author.mention}'s hand: {format_hand(game['player_hand'])} (Total: {hand_value(game['player_hand'])})")
    await ctx.send(f"Dealer's visible card: {game['dealer_hand'][0]['rank']} of {game['dealer_hand'][0]['suit']}")
    await ctx.send("Type `!hit` to take another card or `!stand` to hold your hand.")

def format_hand(hand):
    return ', '.join(f"{card['rank']} of {card['suit']}" for card in hand)

@bot.command()
async def hit(ctx):
    if ctx.author.id not in active_games:
        await ctx.send("You need to start a game with `!blackjack`.")
        return
    game = active_games[ctx.author.id]
    game["player_hand"].append(game["deck"].pop())
    player_value = hand_value(game["player_hand"])
    await ctx.send(f"{ctx.author.mention}'s hand: {format_hand(game['player_hand'])} (Total: {player_value})")
    if player_value > 21:
        await ctx.send(f"{ctx.author.mention}, you busted! Dealer wins.")
        end_game(ctx.author.id, lost=True)

@bot.command()
async def stand(ctx):
    if ctx.author.id not in active_games:
        await ctx.send("You need to start a game with `!blackjack`.")
        return
    game = active_games[ctx.author.id]
    dealer_value = hand_value(game["dealer_hand"])
    while dealer_value < 17:
        game["dealer_hand"].append(game["deck"].pop())
        dealer_value = hand_value(game["dealer_hand"])
    await ctx.send(f"Dealer's final hand: {format_hand(game['dealer_hand'])} (Total: {dealer_value})")
    player_value = hand_value(game["player_hand"])
    if dealer_value > 21 or player_value > dealer_value:
        await ctx.send(f"{ctx.author.mention} wins! You receive {game['bet'] * 2} points!")
        end_game(ctx.author.id, won=True)
    else:
        await ctx.send(f"{ctx.author.mention} lost! Better luck next time.")
        end_game(ctx.author.id, lost=True)

def end_game(user_id, won=False, lost=False):
    game = active_games.pop(user_id, None)
    if not game:
        return
    points = load_points()
    if won:
        points[str(user_id)] = points.get(str(user_id), 0) + game['bet'] * 2
    elif lost:
        taken_points = load_taken_points()
        taken_points["total_taken_points"] += game['bet']
        save_taken_points(taken_points)
    save_points(points)

with open('token.txt', 'r') as token_file:
    bot_token = token_file.read().strip()

bot.run(bot_token)
