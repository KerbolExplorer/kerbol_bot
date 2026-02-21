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

    @app_commands.command(name="flightplan", description="Fetches the latest simbrief flightplan")
    @app_commands.describe(
        simbrief_id="Your Simbrief id, only required the first time running the command."
    )
    async def flightplan(self, interaction:discord.Interaction, simbrief_id:str=None):
        await interaction.response.defer()
        flpn:FlightPlan = await fetch_flightplan(simbrief_id)
        if flpn is None:
            await interaction.followup.send("No flightplan available")
            return
        
        general_embed = discord.Embed(
            title=f"{flpn.icao_airline}{flpn.flight_number}({flpn.callsign}) | {flpn.aircraft} - General Flightplan Information",
            description=f"**Route: {flpn.origin} → {flpn.destination} (ALT {flpn.alternate}) **\n```{flpn.route}```",
            color=discord.Color.blue()
        )
        general_embed.add_field(name="Departure Time:", value=flpn.sanitize_times(flpn.departure_time))
        general_embed.add_field(name="Arrival Time:", value=flpn.sanitize_times(flpn.arrival_time))
        general_embed.add_field(name="Block Time:", value=flpn.sanitize_times(flpn.block_time))
        general_embed.add_field(name="Departure Category:", value=flpn.origin_cat.upper())
        general_embed.add_field(name="Arrival Category:", value=flpn.destination_cat.upper())
        general_embed.add_field(name="Initial Altitude:", value=flpn.initial_alt)
        general_embed.add_field(name="Take Off Weight:", value=f"{flpn.tow}kg")
        general_embed.add_field(name="Zero Fuel Weight:", value=f"{flpn.zfw}kg")
        general_embed.add_field(name="Block Fuel:", value=f"{flpn.block_fuel}kg")
        general_embed.add_field(name="Cargo:", value=f"{flpn.cargo}kg")
        general_embed.add_field(name="Cost Index:", value=flpn.cost_index)
        general_embed.add_field(name="Pax count:", value=f"{flpn.passengers}")
        general_embed.set_footer(text=f"Release number: {flpn.release}")

        alternate_embed = discord.Embed(
            title=f"{flpn.icao_airline}{flpn.flight_number}({flpn.callsign}) | {flpn.aircraft} - Alternate Airport Information",
            description=f"**Alternate Route:**\n ```{flpn.alt_route}```\n**Alternate METAR:**\n```{flpn.alternate_metar}```",
            color=discord.Color.blue()
        )
        alternate_embed.add_field(name="Main Alternate:", value=flpn.alternate)
        alternate_embed.add_field(name="Alternate Distance:", value=f"{flpn.alt_distance}nm")
        alternate_embed.add_field(name="Alternate Category:", value=flpn.alternate_cat.upper())
        alternate_embed.add_field(name="Take Off Alternate", value=flpn.to_alternate)
        alternate_embed.add_field(name="Enroute Alternate", value=flpn.rte_alternate)

        performance_embed = discord.Embed(
            title=f"{flpn.icao_airline}{flpn.flight_number}({flpn.callsign}) | {flpn.aircraft} - Performance Information",
            color=discord.Color.blue()
        )
        performance_embed.add_field(name="Take Off Weight:", value=f"{flpn.tow}kg")
        performance_embed.add_field(name="Zero Fuel Weight:", value=f"{flpn.zfw}kg")
        performance_embed.add_field(name="Block Fuel:", value=f"{flpn.block_fuel}kg")
        performance_embed.add_field(name="Reserve Fuel:", value=f"{flpn.reserve_fuel}kg")
        performance_embed.add_field(name="Cargo:", value=f"{flpn.cargo}kg")
        performance_embed.add_field(name="Cost Index:", value=flpn.cost_index)
        performance_embed.add_field(name="Pax count:", value=f"{flpn.passengers}/{flpn.max_passengers}")
        performance_embed.add_field(name="Engines:", value=flpn.engines)
        performance_embed.add_field(name="Equipment Category:", value=flpn.equip_cat)
        performance_embed.add_field(name="Cruising Altitude:", value=flpn.initial_alt)
        performance_embed.add_field(name="Step Climbs:", value=flpn.stepclimbs)
        performance_embed.add_field(name="Cruise Winds:", value=f"{flpn.wind_dir}º/{flpn.wind_speed}kts")


        weather_embed = discord.Embed(
            title=f"{flpn.icao_airline}{flpn.flight_number}({flpn.callsign}) | {flpn.aircraft} - Weather Information",
            description=f"""**Departure Airport({flpn.origin}) METAR:**
            ```{flpn.origin_metar}```\n
            **Arrival Airport({flpn.destination}) METAR: **
            ```{flpn.destination_metar}```\n
            **Alternate({flpn.alternate}) METAR:**\n
            ```{flpn.alternate_metar}```\n
            **Take Off Alternate({flpn.to_alternate}) METAR:**\n
            ```{flpn.to_alt_metar}```\n
            **Enroute Alternate({flpn.rte_alt_metar}) METAR:**\n
            ```{flpn.rte_alt_metar}```""",
            color=discord.Color.blue()
        )

        embeds = (general_embed, performance_embed, alternate_embed, weather_embed)

        class EmbedView(discord.ui.View):         # select 0 = General, select 1 = Performance, select 2 = Alternate, select 3 = Weather
            def __init__(self, embeds):
                super().__init__()
                self.embeds = embeds
            
            @discord.ui.select(
                placeholder = "Select an option:",
                min_values = 1,
                max_values = 1,
                options = [
                    discord.SelectOption(
                        label = "General Information",
                        description= "Shows general information",
                        emoji = "📝"
                    ),
                    discord.SelectOption(
                        label = "Performance",
                        description = "Shows performance data",
                        emoji = "✈️"
                    ),
                    discord.SelectOption(
                        label= "Alternates",
                        description = "Shows weather data",
                        emoji = "🛬"
                    ),
                    discord.SelectOption(
                        label = "Weather",
                        description = "Shows alternate data",
                        emoji = "🌦️"
                    )
                ]
            )
            async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                index = ["General Information", "Performance", "Alternates", "Weather"].index(select.values[0])
                await interaction.response.edit_message(embed=self.embeds[index], view=self)
        
        await interaction.followup.send(view=EmbedView(embeds), embed=general_embed)


async def setup(bot):
    await bot.add_cog(Schedule(bot))