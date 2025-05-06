import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import random
import os
from .Aviation_Utils.Aviation_Utils import random_flight

db_airport_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airports.db")

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="random_regional_flight", description="Returns a random regional flight")
    @app_commands.describe(country="ISO code of the country")
    async def random_regional_flight(self, interaction:discord.Interaction, country: str):
        
        flight = random_flight(country)
        await interaction.response.send_message(f"A flight has been selected from {flight[0][1]} ({flight[0][0]}) to {flight[1][1]} ({flight[1][0]}) with a distance of {int(flight[2])}nm")



async def setup(bot):
    await bot.add_cog(Schedule(bot))