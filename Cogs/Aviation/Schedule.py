import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import random
import os
from .Aviation_Utils.Aviation_Utils import random_flight, fetch_flightplan, FlightPlan

db_airport_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airports.db")

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="random_regional_flight", description="Returns a random regional flight")
    @app_commands.describe(
        country="ISO code of the country",
        departure_airport="The airport you want to depart from",
        arrival_airport="The airport you want to arrive to",
        min_distance="The minimum distance of the flight, note that this might be decreased if the bot can't find a flight within set parameters",
        max_distance= "The maximum distance of the flight, note that this might be decreased if the bot can't find a flight within set parameters"
        )
    async def random_regional_flight(self, interaction:discord.Interaction, country: str, departure_airport : str = None, arrival_airport: str = None, min_distance: int = None, max_distance: int = None):
        await interaction.response.defer()

        flight = random_flight(country, False, departure_airport, arrival_airport, min_distance, max_distance)
        if flight == None:
            await interaction.followup.send("Could not find any valid flights", ephemeral=True)
        elif flight == 1:
            await interaction.followup.send("You have somehow found a country with a single airport")
        elif flight == 2:
            await interaction.followup.send("The first airport is not valid", ephemeral=True)
        elif flight == 3:
            await interaction.followup.send("The second airport is not valid", ephemeral=True)
        else:
            await interaction.followup.send(f"A flight has been selected from {flight[0][1]} ({flight[0][0]}) to {flight[1][1]} ({flight[1][0]}) with a distance of {int(flight[2])}nm")

    @app_commands.command(name="flightplan", description="Fetches a simbrief flightplan")
    async def flightplan(self, interaction:discord.Interaction, simbrief_id:str=None):
        await interaction.response.defer()
        flpn:FlightPlan = await fetch_flightplan(simbrief_id)
        if flpn is None:
            await interaction.followup.send("No flightplan available")
            return
        
        embed = discord.Embed(
            title=f"{flpn.icao_airline}{flpn.flight_number} | {flpn.aircraft}",
            description=f"**Route: {flpn.origin} → {flpn.destination} (ALT {flpn.alternate}) **\n```{flpn.route}```",
            color=discord.Color.blue()
        )
        embed.add_field(name="**Flight Summary**", value=(
            f"DEP {flpn.departure_time}  ARR {flpn.arrival_time}  ETE {flpn.block_time}\n"
            f"CRZ FL{flpn.initial_alt}  M{flpn.cruise_mach}  CI {flpn.cost_index}  ETOPS: {flpn.is_etops}\n"
            f"PAX {flpn.passengers}  CARGO {flpn.cargo} kg\n"
            f"ZFW {flpn.zfw}  TOW {flpn.tow}  LDW {flpn.ldw}\n"
            f"FUEL {flpn.block_fuel} kg  DIST {flpn.air_distance} nm\n"
            f"ROUTE: {flpn.route}\n"
            f"ALT RTE: {flpn.alt_route}\n"
            f"CAPT {flpn.captain} | DSP {flpn.dispatcher} | REL {flpn.release}"
        ), inline = False)
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Schedule(bot))