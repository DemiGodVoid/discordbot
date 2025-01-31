import discord
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import os
import random

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

model_name = 'microsoft/DialoGPT-medium'
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

def generate_response(prompt):
    prompt = f"Human: {prompt}\nAI:"
    response = generator(prompt, max_length=150, num_return_sequences=1, temperature=0.7, top_k=50)
    return response[0]['generated_text'].split("AI:")[1].strip()

def get_random_insult():
    with open("insult.txt", "r") as file:
        insults = file.readlines()
    return random.choice(insults).strip()

def is_sad(message):
    sad_keywords = ['sad', 'depressed', 'unhappy', 'feeling low', 'crying', 'miserable', 'down', 'heartbroken']
    return any(keyword in message.lower() for keyword in sad_keywords)

class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Respond to insults
        if 'insult' in message.content.lower():
            bot_reply = get_random_insult()
            await message.channel.send(bot_reply)

        # Respond to sadness
        elif is_sad(message.content):
            cheer_up_replies = [
                "Hey, things will get better! You've got this!",
                "I know it's tough, but you're stronger than you think!",
                "I'm here for you! Let's turn that frown upside down!",
                "Sending you positive vibes! You'll feel better soon!"
            ]
            bot_reply = random.choice(cheer_up_replies)
            await message.channel.send(bot_reply)

        # Respond only to 'death' in the message
        elif 'death' in message.content.lower():
            user_message = message.content
            bot_reply = generate_response(user_message)
            await message.channel.send(bot_reply)

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    discord_token = load_token()
    client = MyClient(intents=intents)
    client.run(discord_token)
