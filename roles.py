import discord
from discord.ext import commands
from discord import Intents, Embed

intents = Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
emoji_list = ["🔥", "💪", "🎯", "🚀", "🎨", "💻", "🎮", "🎶", "📚", "💡"]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def roles(ctx):
    embed = Embed(title="Available Roles", description="Tap to receive a role!", color=discord.Color.blue())
    roles = [role for role in ctx.guild.roles if not any(bad in role.name.lower() for bad in ["admin", "bot", "owner"]) and role.name != "@everyone"]

    if not roles:
        await ctx.send("No available roles to display.")
        return

    role_emoji_map = {}

    for index, role in enumerate(roles):
        emoji = emoji_list[index % len(emoji_list)]
        embed.add_field(name=role.name, value=f"Tap {emoji} to receive **{role.name}**", inline=False)
        role_emoji_map[emoji] = role

    message = await ctx.send(embed=embed)

    for emoji in role_emoji_map.keys():
        await message.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in role_emoji_map and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            role = role_emoji_map[str(reaction.emoji)]
            await user.add_roles(role)
            await ctx.send(f"{user.mention} You have been given the **{role.name}** role!")
        except Exception:
            break

    await ctx.send("Role selection timed out.")

with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

bot.run(TOKEN)
