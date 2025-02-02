import discord
import asyncio
import os
import random
import cohere

# Load token from file or prompt for it if not found
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

# Load Cohere API key from file or prompt for it if not found
def load_cohere_api_key():
    if os.path.exists("cohere_api_key.txt"):
        with open("cohere_api_key.txt", "r") as file:
            api_key = file.read().strip()
        print("Cohere API key loaded from cohere_api_key.txt.")
    else:
        api_key = input("Please enter your Cohere API key: ")
        with open("cohere_api_key.txt", "w") as file:
            file.write(api_key)
        print("Cohere API key saved to cohere_api_key.txt.")
    return api_key

# Initialize Cohere API client
cohere_api_key = load_cohere_api_key()
co = cohere.Client(cohere_api_key)

# Set up the bot client
class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.last_sent_message = None  # To track the last sent message
        self.is_active = False  # Track whether bot should respond to messages

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Check for start/stop commands
        if message.content.lower() == "!start":
            self.is_active = True
            await message.channel.send("The bot is now active and will respond to messages!")
        
        elif message.content.lower() == "!stop":
            self.is_active = False
            await message.channel.send("The bot is now inactive and will stop responding to messages.")
        
        # Respond to messages if bot is active
        if self.is_active:
            try:
                bot_reply = generate_response(message.content)
                await message.channel.send(bot_reply)
            except Exception as e:
                await message.channel.send(f"Error occurred: {str(e)}")

    async def send_random_message(self):
        channel_id = 1335020264093651066  # Provided channel ID
        channel = self.get_channel(channel_id)

        if not channel:
            print("Channel not found!")
            return

        while True:
            # Random interval between 1 and 10 minutes (in seconds)
            interval = random.randint(60, 600)  # 60 to 600 seconds (1 to 10 minutes)
            await asyncio.sleep(interval)

            # Generate a random response using the GPT model
            bot_reply = generate_response("Generate a random reply")

            print(f"Generated reply: {bot_reply}")  # Debugging line to check the generated reply

            # Check if the generated response is the same as the last message sent
            if bot_reply == self.last_sent_message:
                print("Duplicate message detected, regenerating.")  # Debugging line
                continue  # Skip sending the same message

            if channel:
                await channel.send(bot_reply)
                self.last_sent_message = bot_reply  # Update the last sent message

# Generate response using Cohere API
def generate_response(prompt):
    try:
        # Replace 'command-xlarge' with the correct model name for your access level
        response = co.generate(
            model='command-xlarge',  # This is the model to use; adjust if needed
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.generations[0].text.strip()  # Access the generated text correctly
    except Exception as e:
        return f"Error occurred: {str(e)}"

# Main entry point to run the bot
if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    discord_token = load_token()
    client = MyClient(intents=intents)
    client.run(discord_token)
