import discord
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import os
import random

# Function to load or ask for the Discord token
def load_token():
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as file:
            token = file.read().strip()
        print("Token loaded from token.txt.")
    else:
        token = input("Please enter your Discord token: ")
        with open("token.txt", "w") as file:
            file.write(token)
        print("Token saved to token.txt.")
    return token

# Initialize the text-generation pipeline with DialoGPT
model_name = 'microsoft/DialoGPT-medium'
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

# Function to generate a response using the model
def generate_response(prompt):
    prompt = f"Human: {prompt}\nAI:"
    response = generator(prompt, max_length=150, num_return_sequences=1, temperature=0.7, top_k=50)
    return response[0]['generated_text'].split("AI:")[1].strip()

# Function to get a random insult from insult.txt
def get_random_insult():
    with open("insult.txt", "r") as file:
        insults = file.readlines()
    return random.choice(insults).strip()

# Create a subclass of discord.Client to interact with the bot
class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Check if the message contains the word 'insult'
        if 'insult' in message.content.lower():
            # Get a random insult and send it
            bot_reply = get_random_insult()
            await message.channel.send(bot_reply)

        # Handle general conversations, i.e., 'death' queries for GPT-style responses
        elif 'death' in message.content.lower():  
            user_message = message.content
            bot_reply = generate_response(user_message)
            await message.channel.send(bot_reply)

        # If the message doesn't include 'death' or 'insult', just respond with a general GPT reply
        else:
            user_message = message.content
            bot_reply = generate_response(user_message)
            await message.channel.send(bot_reply)

# Main part of the bot setup
if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True  # Enable reading message content

    discord_token = load_token()  # Load token from file or ask for it
    client = MyClient(intents=intents)  # Pass intents when creating the client
    client.run(discord_token)  # Run the bot with the token
