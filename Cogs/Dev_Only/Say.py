import discord
from discord import app_commands
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="say", description="[DEV ONLY COMMAND] Have Solgaleo say something for you")
    async def say(self, interaction:discord.Interaction, message: str):
        if interaction.user.id != 442728041115025410:
            await interaction.response.send_message("Only Kerbol can use this command!", ephemeral=True)
            return
        await interaction.channel.send(message)

async def setup(bot):
    await bot.add_cog(Say(bot))