import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os
from .Aviation_Utils.Aviation_Utils import airport_lookup, airport_distance

db_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airports.db")

class Airport_Lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="airport", description="Gives data about an airport")
    @app_commands.describe(airport="The Icao code of the airport we want to see")
    async def airport(self, interaction:discord.Interaction, airport: str):
        airport = airport_lookup(airport)
        if airport == False:
            await interaction.response.send_message("That airport doesn't exist or is not in my database")
        else:
            await interaction.response.send_message("The airport is {}, in {}, latitude is {}, longitude is {}, elevation {}, country {}, airport type: {}".format(airport[0][3], airport[0][10], airport[0][4], airport[0][5], airport[0][6], airport[0][8], airport[0][2]))
    
    @app_commands.command(name="airport_distance", description="Calculates the distance between two airports")
    @app_commands.describe(
        first_airport="The icao code of the first airport",
        second_airport="The icao code of the second airport"
    )
    async def airport_distance(self, interaction:discord.Interaction, first_airport: str, second_airport: str):
        result = airport_distance(first_airport, second_airport)
        if result is False:
            await interaction.response.send_message("One of the two airports either doesn't exist or I don't have it in my database")
        else:
            await interaction.response.send_message(f"The distance between {first_airport} and {second_airport} is {int(result)}nm")



async def setup(bot):
    await bot.add_cog(Airport_Lookup(bot))