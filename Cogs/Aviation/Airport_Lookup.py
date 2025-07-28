import discord
from discord import app_commands
from discord.ext import commands
import os
from .Aviation_Utils.Aviation_Utils import airport_lookup, airport_distance, get_metar

db_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airports.db")

class Airport_Lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="airport", description="Gives data about an airport")
    @app_commands.describe(airport="The Icao code of the airport we want to see")
    async def airport(self, interaction:discord.Interaction, airport: str):
        await interaction.response.defer()
        airport = airport_lookup(airport)
        if airport == False:
            await interaction.followup.send("That airport doesn't exist or is not in my database")
        else:
            metar = get_metar(airport[0][1])

            if metar == False or metar == None:
                metar = "No metar data available"   #Check if there is a metar

            embed = discord.Embed(
                title=f"Information for `{airport[0][1].upper()}`",
                description=f"**Current Metar: **\n```{metar}```",
                color=discord.Color.blue()
            )
            embed.add_field(name="**Airport Data:**", value=(
                f"**Airport Name** : {airport[0][3]}\n"
                f"**Location** : {airport[0][10]}\n"
                f"**Latitude** : {airport[0][4]}\n"
                f"**Longitude** : {airport[0][5]}\n"
                f"**Elevation** : {airport[0][6]}\n"
                f"**Country** : {airport[0][8]}\n"
                f"**Airport Type** : {airport[0][2]}"
            ))
            embed.set_footer(text="Metar source: https://aviationweather.gov/api/data/metar. If you require a summary of the metar use /metar. For flight simulation use only")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="airport_distance", description="Calculates the distance between two airports")
    @app_commands.describe(
        first_airport="The icao code of the first airport",
        second_airport="The icao code of the second airport"
    )
    async def airport_distance(self, interaction:discord.Interaction, first_airport: str, second_airport: str):
        import aiosqlite

        await interaction.response.defer()

        first_airport = first_airport.upper()
        second_airport = second_airport.upper()

        db = await aiosqlite.connect(db_path)
        cursor = await db.cursor()

        sql = "SELECT ident, latitude_deg, longitude_deg FROM airports WHERE ident = ?"
        await cursor.execute(sql, (first_airport,))
        first_airport = await cursor.fetchone()
        if first_airport == []:
            await db.close()
            interaction.followup.send(f"Airport {first_airport} is not valid")
            return
        else:
            first_cords = (first_airport[1], first_airport[2])
        
        sql = "SELECT ident, latitude_deg, longitude_deg FROM airports WHERE ident = ?"
        await cursor.execute(sql, (second_airport,))
        second_airport = await cursor.fetchone()
        if second_airport == []:
            await db.close()
            interaction.followup.send(f"Airport {second_airport} is not valid")
            return
        else:
            second_cords = (second_airport[1], second_airport[2])

        result = airport_distance(first_cords, second_cords)
        await interaction.followup.send(f"The distance between `{first_airport[0]}` and `{second_airport[0]}` is {int(result)}nm")



async def setup(bot):
    await bot.add_cog(Airport_Lookup(bot))