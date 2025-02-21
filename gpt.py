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
        self.chat_history = {}  # Dictionary to store user chat history

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.lower().startswith("!chat"):
            user_message = message.content[6:].strip()
            user_id = message.author.id  # Unique user ID

            if user_message:
                try:
                    bot_reply = self.generate_response(user_id, user_message)
                    bot_reply = bot_reply.replace("Cohere", "Discord bot")  # Replace "Cohere" with "Discord bot"
                    await self.send_long_message(message.channel, bot_reply)
                except Exception as e:
                    await message.channel.send(f"Error occurred: {str(e)}")

    def generate_response(self, user_id, user_message):
        """Generates a response while maintaining conversation history with a rude/sarcastic tone"""
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []  # Create a new history for the user

        # Append latest message to history
        self.chat_history[user_id].append(f"User: {user_message}")

        # Keep only the last 10 exchanges to avoid excessive memory use
        self.chat_history[user_id] = self.chat_history[user_id][-10:]

        # Create full chat history for context with a rude tone
        history_text = "\n".join(self.chat_history[user_id]) + "\nBot (rude):"

        try:
            response = co.generate(
                model='command-xlarge',
                prompt=history_text + " Respond in a rude, sarcastic, or blunt manner.",
                max_tokens=500,
                temperature=0.9
            )

            bot_reply = response.generations[0].text.strip()
            self.chat_history[user_id].append(f"Bot: {bot_reply}")  # Save bot response

            return bot_reply
        except Exception as e:
            return f"Error occurred: {str(e)}"

    async def send_long_message(self, channel, text):
        """Splits long messages and ensures continuation until the message is fully sent"""
        max_length = 2000
        parts = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        for part in parts:
            await channel.send(part)
            await asyncio.sleep(1)  # Small delay to ensure proper order

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    discord_token = load_token()
    client = MyClient(intents=intents)
    client.run(discord_token)
