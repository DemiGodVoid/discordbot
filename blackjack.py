import discord
from discord.ext import commands
import random
import json

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.dm_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

points_file = 'points.json'
active_game = False
players = []
bets = {}
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

def shuffle_deck():
    global deck
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    deck = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]
    random.shuffle(deck)

def deal_hand():
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
    global active_game, players, bets
    if active_game:
        await ctx.send("A game is already in progress!")
        return
    active_game = True
    players = []
    bets = {}
    await ctx.send("Starting blackjack! Say .one for player one and .two for player two.")

@bot.command()
async def one(ctx):
    global players
    if active_game and len(players) < 1:
        players.append(ctx.author)
        await ctx.send(f"{ctx.author.mention} joined as Player 1!")

@bot.command()
async def two(ctx):
    global players
    if active_game and len(players) == 1:
        players.append(ctx.author)
        await ctx.send(f"{ctx.author.mention} joined as Player 2!")
        await ctx.send(f"{players[0].mention}, enter your bet amount!")

@bot.command()
async def bet(ctx, amount: int):
    global players, bets
    if ctx.author not in players or ctx.author in bets:
        return
    points = load_points()
    if str(ctx.author.id) not in points or points[str(ctx.author.id)] < amount:
        await ctx.send(f"{ctx.author.mention}, you don't have enough points!")
        return
    bets[ctx.author] = amount
    points[str(ctx.author.id)] -= amount
    save_points(points)
    await ctx.send(f"{ctx.author.mention} bet {amount} points!")
    if len(bets) == 2:
        total_bet = sum(bets.values())
        await ctx.send(f"Total bet pool: {total_bet} points. Dealing cards!")
        await start_game()

async def start_game():
    shuffle_deck()
    hands = {players[0]: deal_hand(), players[1]: deal_hand()}
    for player, hand in hands.items():
        cards = ', '.join(f"{card['rank']} of {card['suit']}" for card in hand)
        await player.send(f"Your hand: {cards}")
    await bot.get_channel(players[0].guild.id).send("Cards dealt! Check your DMs!")
    await determine_winner(hands)

async def determine_winner(hands):
    global active_game
    values = {player: hand_value(hand) for player, hand in hands.items()}
    winner = max(values, key=values.get) if values[players[0]] != values[players[1]] else None
    points = load_points()
    if winner:
        total_bet = sum(bets.values())
        points[str(winner.id)] += total_bet
        await bot.get_channel(players[0].guild.id).send(f"{winner.mention} wins and gets {total_bet} points!")
    else:
        await bot.get_channel(players[0].guild.id).send("It's a tie! Bets are returned.")
        for player, bet in bets.items():
            points[str(player.id)] += bet
    save_points(points)
    active_game = False

with open('token.txt', 'r') as token_file:
    bot_token = token_file.read().strip()

bot.run(bot_token)
