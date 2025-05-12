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
    async def random_regional_flight(self, interaction:discord.Interaction, country: str, departure_airport : str = None, arrival_airport: str = None):
        
        flight = random_flight(country, False, departure_airport, arrival_airport)
        if flight == None:
            await interaction.response.send_message("Could not find any valid flights for that country", ephemeral=True)
        elif flight == 1:
            await interaction.response.send_message("You have somehow found a country with a single airport")
        elif flight == 2:
            await interaction.response.send_message("The first airport is not valid", ephemeral=True)
        elif flight == 3:
            await interaction.response.send_message("The second airport is not valid", ephemeral=True)
        else:
            await interaction.response.send_message(f"A flight has been selected from {flight[0][1]} ({flight[0][0]}) to {flight[1][1]} ({flight[1][0]}) with a distance of {int(flight[2])}nm")



async def setup(bot):
    await bot.add_cog(Schedule(bot))