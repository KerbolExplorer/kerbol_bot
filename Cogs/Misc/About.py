import discord
from discord import app_commands
from discord.ext import commands

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="about", description="General info on the bot")
    async def about(self, interaction:discord.Interaction):
        embed = discord.Embed(
            color=0xf1c40f, title="About", description="""Version 1.0-alpha. Bot developed by Kerbol (kobalt.621). 
            The bot is open source, link to the github: https://github.com/KerbolExplorer/kerbol_bot. 
            **Known Issues**:
            -> The music commands have been removed indefinetely due to issues with youtube.
            -> Leaderboard is limited to top 10 users.
            -> Metar_request does whatever it wants when it comes to timing.
            """
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(About(bot))