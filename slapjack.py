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
        with open("points.json", "r") as file:
            return json.load(file)
    return {}

def save_points(points):
    with open("points.json", "w") as file:
        json.dump(points, file)

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
        
        await message.channel.send("Are you Player 1 or Player 2? Type `.1` or `.2`.")
        games[message.channel.id] = {"player1": None, "player2": None, "deck": create_deck(), "players": {}, "pile": []}
    
    elif content == ".1":
        game = games.get(message.channel.id)
        if not game:
            await message.channel.send("No active game! Start one with `.slap_jack`.")
            return

        if game["player1"] is None:
            game["player1"] = message.author.id
            await message.channel.send(f"{message.author.display_name} joined as Player 1! Now, Player 2, type `.2` to join.")
        else:
            await message.channel.send("Player 1 has already joined!")
    
    elif content == ".2":
        game = games.get(message.channel.id)
        if not game:
            await message.channel.send("No active game! Start one with `.slap_jack`.")
            return
        
        if game["player2"] is None:
            game["player2"] = message.author.id
            await message.channel.send(f"{message.author.display_name} joined as Player 2! Both players are ready.")
            await message.channel.send(f"{message.guild.get_member(game['player1']).mention}, enter your amount (50k or more).")
        else:
            await message.channel.send("Player 2 has already joined!")
    
    elif message.author.id in [g.get("player1"), g.get("player2")] and content.isdigit():
        game = games.get(message.channel.id)
        amount = int(content)
        if amount < 50000:
            await message.channel.send("You have to enter 50k points or more!")
            return
        
        if message.author.id == game["player1"]:
            game["bet1"] = amount
            await message.channel.send(f"{message.guild.get_member(game['player2']).mention}, enter your amount (50k or more).")
        else:
            game["bet2"] = amount
            total = game["bet1"] + game["bet2"]
            player1_points = points.get(str(game["player1"]), 0)
            player2_points = points.get(str(game["player2"]), 0)
            
            if player1_points < game["bet1"] or player2_points < game["bet2"]:
                await message.channel.send("One or both players do not have enough points. Game cancelled.")
                del games[message.channel.id]
                return
            
            points[str(game["player1"])] -= game["bet1"]
            points[str(game["player2"])] -= game["bet2"]
            save_points(points)
            
            await message.channel.send(f"{message.guild.get_member(game['player1']).mention} gave {game['bet1']} points, {message.guild.get_member(game['player2']).mention} gave {game['bet2']} points. Total amount is {total} points! Let the game begin!")
    
    elif content.startswith(".play"):
        game = games.get(message.channel.id)
        if not game:
            await message.channel.send("No active game! Start one with `.slap_jack`.")
            return
        
        if message.author.id not in game["players"]:
            await message.channel.send("You're not in the game! Join with `.1` or `.2`.")
            return
        
        if not game["deck"]:
            await message.channel.send("The deck is empty! The game is over.")
            return
        
        card = game["deck"].pop(0)
        game["pile"].append(card)
        await message.channel.send(f"{message.author.display_name} played {card}!")

token = get_token()
client.run(token)
