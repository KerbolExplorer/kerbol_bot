import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import random
import os
from .Aviation_Utils.Aviation_Utils import airport_lookup, airport_distance

db_airport_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airports.db")

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="random_regional_flight", description="Returns a random regional flight")
    @app_commands.describe(country="ISO code of the country")
    async def random_regional_flight(self, interaction:discord.Interaction, country: str):
        country = country.upper()

        airport_db = sqlite3.connect(db_airport_path)
        airport_cursor = airport_db.cursor()

        sql = "SELECT * FROM airports WHERE iso_country = ? AND (type != 'heliport' AND type != 'closed')"
        airport_cursor.execute(sql, (country,))
        airport_choices = airport_cursor.fetchall()

        if airport_choices == []:
            await interaction.response.send_message("No airports where found in the specified country")
            airport_db.close()
            return
        elif len(airport_choices) == 1:
            await interaction.response.send_message("There is only one airport in this country")
            airport_db.close()            
            return
        
        airport_db.close()

        attempts = 100

        departure_airport_code = None
        destination_airport_code = None

        while attempts >= 0:
            departure_airport = airport_choices[random.randint(0, (len(airport_choices) -1))]
            if departure_airport[12] != '':
                departure_airport_code = departure_airport[12]
                break
            elif departure_airport[14] != '':
                departure_airport_code = departure_airport[14]
                break
            elif departure_airport[1] != '':
                departure_airport_code = departure_airport[1]
                break
            else:
                attempts -= 1

        if attempts < 0:
            await interaction.response.send_message("No valid airports where found.")
            return


        attempts = 100
        while attempts >= 0:
            destination_airport = airport_choices[random.randint(0, (len(airport_choices) -1))]
            if destination_airport[12] != '':
                destination_airport_code = destination_airport[12]
                break
            elif destination_airport[14] != '':
                destination_airport_code = destination_airport[14]
                break
            elif destination_airport[1] != '':
                destination_airport_code = destination_airport[1]
                break
            else:
                attempts -= 1        
        
        if attempts < 0:
            await interaction.response.send_message("No valid airports where found.")
            return

        distantance = airport_distance(departure_airport_code, destination_airport_code)

        await interaction.response.send_message(f"A flight has been selected from {departure_airport_code} ({departure_airport[3]}) to {destination_airport_code} ({destination_airport[3]}) with a distance of {int(distantance)}nm")



async def setup(bot):
    await bot.add_cog(Schedule(bot))