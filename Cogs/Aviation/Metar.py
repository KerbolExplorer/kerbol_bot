import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
from .Aviation_Utils.Aviation_Utils import get_metar

class Metar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @app_commands.command(name="metar", description="Gets the metar for an airport")
    async def metar(self, interaction:discord.Interaction, airport:str):
        metar = get_metar(airport, False)

        if metar == False:
            await interaction.response.send_message("There was an issue getting this metar.", ephemeral=True)
        elif metar == None:
            await interaction.response.send_message("This metar is not available.", ephemeral=True)
        else:

            zulu_time = datetime.fromtimestamp(metar['obsTime'], tz=timezone.utc)
            zulu_time = zulu_time.strftime("%H%MZ")
            if metar['wgst'] is not None:
                wind = f"from {metar['wdir']}º at {metar['wspd']}kt, gusting at {metar['wgst']}kt\n"
            else:
                wind = f"from {metar['wdir']}º at {metar['wspd']}kt\n"
            embed = discord.Embed(
                title=f"METAR: {metar['icaoId']}",
                description=f"**Raw Report**\n```{metar['rawOb']}```",
                color=discord.Color.blue()
            )
            embed.add_field(name="**Data Summary**", value=(
                f"**Station** : {metar['icaoId']} ({metar['name']})\n"
                f"**Observed at** : {zulu_time}\n"
                f"**Wind** : {wind}"
                f"**Visibility** : {metar['visib']}km\n"
                f"**Temperature** : {metar['temp']}ºC\n"
                f"**Dew Point** : {metar['dewp']}ºC\n"
                f"**Altimeter** : {metar['altim']}\n"
                f"**Clouds**: {metar['clouds']}"
            ), inline=False)
            embed.set_footer(text="For flight simulation use only. Source: https://aviationweather.gov/api/data/metar")
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Metar(bot))