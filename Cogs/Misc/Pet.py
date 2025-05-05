import discord
from discord import app_commands
from discord.ext import commands
import random

class Pet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="pet", description="Pet Solgaleo")
    async def pet(self, interaction:discord.Interaction):
        responses = ("**Arff**", "**UwU**", "**:3**", "**Woof**", "**PURRR**", "**Mmmmh**", "**Waff**", "**Wuff**", "**Solll**", "ouch...")
        await interaction.response.send_message(random.choice(responses))


async def setup(bot):
    await bot.add_cog(Pet(bot))