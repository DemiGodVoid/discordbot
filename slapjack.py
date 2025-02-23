import discord
import random
import asyncio
import os
import json

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
client = discord.Client(intents=intents)

def get_token():
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as file:
            return file.read().strip()
    else:
        token = input("Enter your Discord bot token: ")
        with open("token.txt", "w") as file:
            file.write(token)
        return token

def load_points():
    if os.path.exists("points.json"):
        try:
            with open("points.json", "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error: points.json is corrupted. Resetting...")
            return {}
    return {}

def save_points(points):
    with open("points.json", "w") as file:
        json.dump(points, file, indent=4)

games = {}
points = load_points()
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♥", "♦", "♣", "♠"]

def create_deck():
    deck = [f"{value}{suit}" for value in CARD_VALUES for suit in SUITS]
    random.shuffle(deck)
    return deck

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    content = message.content.strip().lower()
    
    if content.startswith(".slap_help"):
        await message.channel.send("Slap Jack Instructions: \n- Use `.slap_jack` to start a game.\n- Players take turns playing cards using `.play`.\n- If a Jack is played, slap it with `.slap`.\n- Last player with cards wins!")
    
    elif content.startswith(".slap_jack"):
        if message.channel.id in games:
            await message.channel.send("A game is already in progress!")
            return
        
        games[message.channel.id] = {
            "player1": None,
            "player2": None,
            "deck": create_deck(),
            "players": {},
            "pile": [],
            "bet1": None,
            "bet2": None,
            "current_turn": None,
            "last_card": None
        }
        
        await message.channel.send("Are you Player 1 or Player 2? Type `.1` or `.2`.")
    
    elif content == ".1":
        game = games.get(message.channel.id)
        if not game:
            await message.channel.send("No active game! Start one with `.slap_jack`.")
            return
        
        if game["player1"] is None:
            game["player1"] = message.author
            await message.channel.send(f"{message.author.display_name} joined as Player 1! Now, Player 2, type `.2` to join.")
        else:
            await message.channel.send("Player 1 has already joined!")
    
    elif content == ".2":
        game = games.get(message.channel.id)
        if not game:
            await message.channel.send("No active game! Start one with `.slap_jack`.")
            return
        
        if game["player2"] is None:
            game["player2"] = message.author
            await message.channel.send(f"{message.author.display_name} joined as Player 2! Both players are ready.")
            
            player1 = game["player1"]
            player2 = game["player2"]
            
            if player1 and player2:
                player1_balance = points.get(str(player1.id), 0)
                await message.channel.send(f"{player1.mention}, enter your amount (50k or more). Your current balance: {player1_balance} points.")
        else:
            await message.channel.send("Player 2 has already joined!")
    
    elif content.isdigit():
        game = games.get(message.channel.id)
        if not game:
            return
        
        amount = int(content)
        user_id = str(message.author.id)
        
        if amount < 50000:
            await message.channel.send("You have to enter 50k points or more!")
            return
        
        if user_id not in points:
            points[user_id] = 0
        
        if points[user_id] < amount:
            await message.channel.send(f"You don't have enough points! You have {points[user_id]} points.")
            return
        
        points[user_id] -= amount
        save_points(points)
        
        if message.author == game.get("player1"):
            game["bet1"] = amount
        elif message.author == game.get("player2"):
            game["bet2"] = amount
        
        if game["bet1"] and game["bet2"]:
            total = game["bet1"] + game["bet2"]
            await message.channel.send(f"Total bet: {total} points! Let the game begin!")
            game["current_turn"] = game["player1"]
    
    elif content.startswith(".play"):
        game = games.get(message.channel.id)
        if not game or message.author != game["current_turn"]:
            await message.channel.send("It's not your turn yet!")
            return
        
        if not game["deck"]:
            await message.channel.send("The deck is empty! The game is over.")
            return
        
        card = game["deck"].pop(0)
        game["pile"].append(card)
        game["last_card"] = card
        
        await message.channel.send(f"{message.author.display_name} played {card}!")
        game["current_turn"] = game["player2"] if game["current_turn"] == game["player1"] else game["player1"]
    
    elif content.startswith(".slap") and games.get(message.channel.id, {}).get("last_card", "").startswith("J"):
        winner = message.author
        total_bet = games[message.channel.id]["bet1"] + games[message.channel.id]["bet2"]
        points[str(winner.id)] += total_bet
        save_points(points)
        await message.channel.send(f"{winner.display_name} slapped the Jack and won {total_bet} points!")
        del games[message.channel.id]
    
    elif content.startswith(".slap"):
        await message.channel.send("No Jack to slap!")
        
client.run(get_token())
