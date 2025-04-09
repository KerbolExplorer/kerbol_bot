import discord
from discord import app_commands
from discord.ext import commands
from .Aviation_Utils.Aviation_Utils import get_metar

class Metar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @app_commands.command(name="metar", description="Gets the metar for an airport")
    async def metar(self, interaction:discord.Interaction, airport:str):
        metar = get_metar(airport)

        if metar == False:
            await interaction.response.send_message("There was an issue getting this metar.", ephemeral=True)
        elif metar == None:
            await interaction.response.send_message("This metar is not available.", ephemeral=True)
        else:
            await interaction.response.send_message(metar)

async def setup(bot):
    await bot.add_cog(Metar(bot))