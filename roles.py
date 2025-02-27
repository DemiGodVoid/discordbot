import discord
from discord.ext import commands
from discord import Intents, Embed

intents = Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

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

    for role in roles:
        embed.add_field(name=role.name, value=f"Tap 🔘 to receive **{role.name}**", inline=False)

    message = await ctx.send(embed=embed)

    for _ in roles:
        await message.add_reaction("🔘")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == "🔘" and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            role_index = list(reaction.message.reactions).index(reaction)
            role = roles[role_index]
            await user.add_roles(role)
            await ctx.send(f"{user.mention} You have been given the **{role.name}** role!")
            return
        except (Exception, IndexError):
            break

    await ctx.send("Role selection timed out.")

with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

bot.run(TOKEN)
