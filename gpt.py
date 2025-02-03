import discord
import asyncio
import os
import cohere

def load_token():
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as file:
            token = file.read().strip()
    else:
        token = input("Please enter your Discord token: ")
        with open("token.txt", "w") as file:
            file.write(token)
    return token

def load_cohere_api_key():
    if os.path.exists("cohere_api_key.txt"):
        with open("cohere_api_key.txt", "r") as file:
            api_key = file.read().strip()
    else:
        api_key = input("Please enter your Cohere API key: ")
        with open("cohere_api_key.txt", "w") as file:
            file.write(api_key)
    return api_key

def load_channel_id():
    if os.path.exists("channel_id.txt"):
        with open("channel_id.txt", "r") as file:
            channel_id = int(file.read().strip())
    else:
        channel_id = input("Please enter the channel ID: ")
        with open("channel_id.txt", "w") as file:
            file.write(str(channel_id))
    return channel_id

cohere_api_key = load_cohere_api_key()
co = cohere.Client(cohere_api_key)

class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.channel_id = load_channel_id()

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.lower().startswith("!chat"):
            user_message = message.content[6:].strip()
            if user_message:
                try:
                    bot_reply = generate_response(user_message)
                    await message.channel.send(bot_reply)
                except Exception as e:
                    await message.channel.send(f"Error occurred: {str(e)}")

def generate_response(prompt):
    try:
        response = co.generate(
            model='command-xlarge',
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Error occurred: {str(e)}"

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    discord_token = load_token()
    client = MyClient(intents=intents)
    client.run(discord_token)
