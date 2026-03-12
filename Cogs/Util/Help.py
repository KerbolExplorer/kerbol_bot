import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Shows information about Orion")
    async def help(self, interaction:discord.Interaction):
        await interaction.response.send_message("Not current implemented")
        

async def setup(bot):
    await bot.add_cog(Help(bot))