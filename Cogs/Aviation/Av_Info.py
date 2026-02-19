import discord
from discord import app_commands
from discord.ext import commands
from .Aviation_Utils.Aviation_Utils import get_navaid

class Av_Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="get_navaid", description="Fetches information on a navaid")
    async def get_navaid(self, interaction:discord.Interaction, navaid:str):
        navaid = get_navaid(navaid)
        print(navaid)

async def setup(bot):
    await bot.add_cog(Av_Info(bot))