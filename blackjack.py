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
    global active_game
    if active_game:
        await ctx.send("A game is already in progress!")
        return
    active_game = True
    await ctx.send(f"{ctx.author.mention}, enter your bet amount!")

@bot.command()
async def bet(ctx, amount: int):
    global active_game
    points = load_points()
    if str(ctx.author.id) not in points or points[str(ctx.author.id)] < amount:
        await ctx.send(f"{ctx.author.mention}, you don't have enough points!")
        active_game = False
        return
    points[str(ctx.author.id)] -= amount
    save_points(points)
    total_pot = amount * 2
    await ctx.send(f"Bet placed: {amount} points. Potential winnings: {total_pot} points. Dealing cards!")
    await start_game(ctx, amount, total_pot)

async def start_game(ctx, bet, total_pot):
    shuffle_deck()
    player_hand = deal_hand()
    dealer_hand = deal_hand()
    await ctx.author.send(f"Your hand: {', '.join(f'{card['rank']} of {card['suit']}' for card in player_hand)}")
    await ctx.send("Cards dealt! Check your DMs!")
    await determine_winner(ctx, player_hand, dealer_hand, bet, total_pot)

async def determine_winner(ctx, player_hand, dealer_hand, bet, total_pot):
    global active_game
    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)
    points = load_points()
    if player_value > dealer_value or dealer_value > 21:
        points[str(ctx.author.id)] += total_pot
        await ctx.send(f"{ctx.author.mention} wins! You receive {total_pot} points!")
    else:
        await ctx.send(f"{ctx.author.mention} lost! Better luck next time.")
    save_points(points)
    active_game = False

with open('token.txt', 'r') as token_file:
    bot_token = token_file.read().strip()

bot.run(bot_token)
