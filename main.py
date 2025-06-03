import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
from views.auth_view import AuthView

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


@bot.event
async def on_ready():
    bot.add_view(AuthView())
    print(f"Бот {bot.user} готов!")


bot.load_extension("cogs.main_menu_cog")

bot.run(os.getenv("DISCORD_TOKEN"))
