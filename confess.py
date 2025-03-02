import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_channel_per_server = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print(f'Connected to {len(bot.guilds)} servers')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.guild:
        last_channel_per_server[message.guild.id] = message.channel
    await bot.process_commands(message)

@bot.command()
async def confess(ctx, *, confession: str):
    if not confession:
        await ctx.send("Please provide a confession message.")
        return

    servers = list(bot.guilds)
    server_list = "\n".join([f"{index+1}. {server.name}" for index, server in enumerate(servers)])
    await ctx.send(f"Select a server to send your confession to by replying with the number:\n{server_list}")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        selected = int(msg.content) - 1
        if 0 <= selected < len(servers):
            selected_server = servers[selected]
            channels = [channel for channel in selected_server.text_channels if channel.permissions_for(selected_server.me).send_messages][:4]
            channel_list = "\n".join([f"{index+1}. {channel.name}" for index, channel in enumerate(channels)])
            if not channels:
                await ctx.send("No accessible text channels in the selected server.")
                return

            await ctx.send(f"Select a channel to send your confession to by replying with the number:\n{channel_list}")

            msg = await bot.wait_for('message', check=check, timeout=30.0)
            selected_channel = int(msg.content) - 1
            if 0 <= selected_channel < len(channels):
                await channels[selected_channel].send(f"From anon person: {confession}")
                await ctx.send("Confession sent!")
            else:
                await ctx.send("Invalid channel number.")
        else:
            await ctx.send("Invalid server number.")
    except TimeoutError:
        await ctx.send("You took too long to respond.")

with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()

bot.run(TOKEN)
