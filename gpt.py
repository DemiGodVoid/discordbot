import discord
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import os

# Function to load or ask for the Discord token
def load_token():
    # Check if token.txt exists
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

# Load the model and tokenizer
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Initialize the text-generation pipeline with adjusted parameters
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

# Function to generate a response using the model
def generate_response(prompt):
    # Add a unique system message to the input to encourage better responses
    prompt = f"Human: {prompt}\nAI:"

    # Generate the response
    response = generator(prompt, max_length=100, num_return_sequences=1, 
                         temperature=0.7, top_k=50)
    
    # Extract the AI's reply and return it, removing the 'AI:' part
    return response[0]['generated_text'].split("AI:")[1].strip()

# Create a subclass of discord.Client to interact with the bot
class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        # Don't let the bot reply to itself
        if message.author == self.user:
            return

        # Check if the message contains the word 'Death'
        if 'death' in message.content.lower():  # Using .lower() to make it case insensitive
            user_message = message.content
            print(f"User: {user_message}")

            # Generate a response using the model
            bot_reply = generate_response(user_message)
            await message.channel.send(bot_reply)

# Main part of the bot setup
if __name__ == "__main__":
    # Set up intents
    intents = discord.Intents.default()
    intents.message_content = True  # Enable reading message content

    discord_token = load_token()  # Load token from file or ask for it
    client = MyClient(intents=intents)  # Pass intents when creating the client
    client.run(discord_token)  # Run the bot with the token
