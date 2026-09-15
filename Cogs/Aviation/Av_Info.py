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
        if navaid == None:
            await interaction.response.send_message("This navaid is not in my database", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"{navaid[3]}:`{navaid[4]}`",
            color=discord.Colour.blue(),
            description=f"Related airport `{navaid[19]}`"
        )
        embed.set_thumbnail(url="https://cdn.creazilla.com/icons/3231339/navaid-vordme-icon-size_256.png")
        embed.add_field(name="**Ident:**", value=f"{navaid[2]}", inline=False)
        embed.add_field(name="**Frequency:**", value=f"{navaid[5]/1000}", inline=False)
        embed.add_field(name="**Coordinates:**", value=f"{navaid[6]}, {navaid[7]}", inline=False)
        embed.add_field(name="**Country:**", value=f"{navaid[9]}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Av_Info(bot))