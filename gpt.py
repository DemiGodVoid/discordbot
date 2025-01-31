import discord
from discord.ext import commands
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os

# Function to get or save the bot token
def get_bot_token():
    token_file = "bot_token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r") as file:
            return file.read().strip()
    else:
        token = input("Enter your bot token: ")
        with open(token_file, "w") as file:
            file.write(token)
        return token

# Set up the bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load GPT-2 model and tokenizer from HuggingFace Transformers
model_name = "gpt2"  # You can switch this to a larger model like "gpt2-medium" or "gpt2-large" if needed
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Function to generate responses using the GPT-2 model
def generate_response(input_text):
    # Encode input and generate output
    inputs = tokenizer.encode(input_text, return_tensors="pt")
    outputs = model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2, top_p=0.92, top_k=50)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def chat(ctx, *, message: str):
    """Talk to a local GPT-2 chatbot!"""
    response = generate_response(message)
    await ctx.send(response)

@bot.command()
async def script(ctx, *, prompt: str):
    """Generate a script using a local GPT-2 model!"""
    script_text = generate_response(f"Write a script about {prompt}")
    await ctx.send(f'```{script_text[:1900]}```')  # Discord message limit

# Run the bot with stored or user-provided token
TOKEN = get_bot_token()
bot.run(TOKEN)
