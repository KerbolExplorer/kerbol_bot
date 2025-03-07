import discord
from discord import app_commands
from discord.ext import commands

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="about", description="General info on the bot")
    async def about(self, interaction:discord.Interaction):
        embed = discord.Embed(
            color=0xf1c40f, title="About", description="""Version 2.0. Bot developed by Kerbol (kobalt.621). 
            The bot is open source, link to the github: [super cool link]. 
            **Known Issues**:
            -> Music may lag when someone adds a song to the queue.
            -> Playlist may take a while to load up on the bot.
            -> Cooldown to gain xp is currently global.
            """
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(About(bot))