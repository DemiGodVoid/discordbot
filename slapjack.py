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
        
        # Initialize a new game with both players set to None
        games[message.channel.id] = {
            "player1": None,
            "player2": None,
            "deck": create_deck(),
            "players": {},
            "pile": [],
            "bet1": None,
            "bet2": None,
            "current_turn": None,  # Add a turn tracker
            "last_card": None  # Keep track of the last card played for slapping
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
            
            # Now both players are set
            player1 = game["player1"]
            player2 = game["player2"]
            
            if player1 and player2:
                # Prompt Player 1 to enter points first
                player1_balance = points.get(str(player1.id), 0)
                await message.channel.send(f"{player1.mention}, enter your amount (50k or more). Your current balance: {player1_balance} points.")
        else:
            await message.channel.send("Player 2 has already joined!")
    
    elif message.author == games[message.channel.id]["player1"] and content.isdigit():
        game = games.get(message.channel.id)
        amount = int(content)
        
        if amount < 50000:
            await message.channel.send("You have to enter 50k points or more!")
            return
        
        # Deduct the points for Player 1
        player1_balance = points.get(str(game["player1"].id), 0)
        if player1_balance < amount:
            await message.channel.send(f"You don't have enough points! You have {player1_balance} points.")
            return
        
        points[str(game["player1"].id)] -= amount
        save_points(points)
        game["bet1"] = amount
        
        player2 = game["player2"]
        if player2:
            await message.channel.send(f"{player2.mention}, enter your amount (50k or more). Your current balance: {points.get(str(player2.id), 0)} points.")
    
    elif message.author == games[message.channel.id]["player2"] and content.isdigit():
        game = games.get(message.channel.id)
        amount = int(content)
        
        if amount < 50000:
            await message.channel.send("You have to enter 50k points or more!")
            return
        
        # Deduct the points for Player 2
        player2_balance = points.get(str(game["player2"].id), 0)
        if player2_balance < amount:
            await message.channel.send(f"You don't have enough points! You have {player2_balance} points.")
            return
        
        points[str(game["player2"].id)] -= amount
        save_points(points)
        game["bet2"] = amount
        
        # Total the bets and announce the result
        total = game["bet1"] + game["bet2"]
        await message.channel.send(f"{game['player1'].mention} gave {game['bet1']} points, {game['player2'].mention} gave {game['bet2']} points. Total amount is {total} points! Let the game begin!")
        
        # Set the first turn to Player 1
        game["current_turn"] = game["player1"]
    
    elif content.startswith(".play"):
        game = games.get(message.channel.id)
        if not game:
            await message.channel.send("No active game! Start one with `.slap_jack`.")
            return
        
        if message.author not in [game["player1"], game["player2"]]:
            await message.channel.send("You're not in the game! Join with `.1` or `.2`.")
            return
        
        if game["current_turn"] != message.author:
            await message.channel.send("It's not your turn yet! Wait for the other player to play.")
            return
        
        if not game["deck"]:
            await message.channel.send("The deck is empty! The game is over.")
            return
        
        card = game["deck"].pop(0)  # Draw a card
        game["pile"].append(card)
        game["last_card"] = card  # Save the last card played
        
        await message.channel.send(f"{message.author.display_name} played {card}!")
        
        # Switch turns
        game["current_turn"] = game["player2"] if game["current_turn"] == game["player1"] else game["player1"]
        
        # Show remaining cards in the deck
        await message.channel.send(f"Cards remaining in deck: {len(game['deck'])}")

    elif content.startswith(".slap"):
        game = games.get(message.channel.id)
        if not game:
            await message.channel.send("No active game! Start one with `.slap_jack`.")
            return
        
        if message.author not in [game["player1"], game["player2"]]:
            await message.channel.send("You're not in the game! Join with `.1` or `.2`.")
            return
        
        if game["last_card"] and game["last_card"].startswith("J"):
            if message.author == game["current_turn"]:
                await message.channel.send(f"{message.author.display_name} slapped the Jack and wins the round!")
                
                # Award the points to the winner
                total_bet = game["bet1"] + game["bet2"]
                if message.author == game["player1"]:
                    points[str(game["player1"].id)] += total_bet
                else:
                    points[str(game["player2"].id)] += total_bet
                save_points(points)
                
                # Reset the game
                del games[message.channel.id]
            else:
                await message.channel.send("It's not your turn to slap the Jack!")
        else:
            await message.channel.send("No Jack to slap!")
        
token = get_token()
client.run(token)
