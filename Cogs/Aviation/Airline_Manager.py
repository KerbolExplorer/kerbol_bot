import discord
from discord import app_commands
from discord.ext import commands
from .Aviation_Utils.Aviation_Utils import airport_lookup, airport_distance
import sqlite3
import os

db_airline_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airlines.db")
db_aircraft_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "aircraft.db")

class Airline_Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        airline_db = sqlite3.connect(db_airline_path)
        airline_cursor = airline_db.cursor()
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='Airline'" #check if the database has a table
        airline_cursor.execute(sql)
        result = airline_cursor.fetchall()  
        if not result:
            sql = f'CREATE TABLE "Airline" (airlineId INTEGER, airlineName TEXT, airlineICAO TEXT, homeBase TEXT, owner INTEGER, money INTEGER)' #if the database doesn't have any table we create it
            airline_cursor.execute(sql)
        airline_db.commit()
        airline_db.close()
    
    @app_commands.command(name="create_airline", description="Creates an airline")
    async def create_airline(self, interaction:discord.Interaction, airline_name: str, airline_icao: str, airline_homebase: str):
        if len(airline_icao) != 3:
            await interaction.response.send_message("The icao code must have 3 letters.", ephemeral=True)
            return

        if airport_lookup(airline_homebase) is False:
            await interaction.response.send_message("The chosen homebase either doesn't exist or is not in my database. Please try another one", ephemeral=True)
            return
        
        airline_db = sqlite3.connect(db_airline_path)
        airline_cursor = airline_db.cursor()

        #Select the airline id, this is done by grabbing the newest airline's id and adding it a 1
        sql = "SELECT * FROM Airline ORDER BY airlineID DESC LIMIT 1"
        airline_cursor.execute(sql)
        airline_id = airline_cursor.fetchall()
        if airline_id == []:
            airline_id = 0
        else:
            airline_id = (airline_id[0][0] + 1) 
        
        #Verify if the user doesn't have more than one airline.
        sql = "SELECT * FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (interaction.user.id,))
        airline_owner = airline_cursor.fetchall()
        if airline_owner != []:
            await interaction.response.send_message("You cant own more than one airline, either make a subsidiary or delete your current one", ephemeral=True)
            return
        else:
            airline_owner = interaction.user.id
        
        #TODO add a modal to confirm airline data before creation.
        sql = "INSERT INTO Airline (airlineId, airlineName, airlineICAO, homeBase, owner) VALUES (?, ?, ?, ? , ?)"
        airline_cursor.execute(sql, (airline_id, airline_name, airline_icao.upper(), airline_homebase.upper(), airline_owner))
        airline_db.commit()
        airline_db.close()
        await interaction.response.send_message("Airline created!")


    @app_commands.command(name="delete_airline", description="Deletes an airline")      #TODO this will later go in the manage airline command
    async def delete_airline(self, interaction:discord.Interaction, airline_name: str):
        airline_db = sqlite3.connect(db_airline_path)
        airline_cursor = airline_db.cursor()

        sql = "SELECT * FROM Airline WHERE airlineName = ?"
        airline_cursor.execute(sql, (airline_name,))

        airline_info = airline_cursor.fetchall()

        if airline_info == []:
            await interaction.response.send_message("This airline doesn't exist", ephemeral=True)
            return

        if airline_info[0][4] != interaction.user.id:
            await interaction.response.send_message("You can't delete an airline that isn't yours!", ephemeral=True)
            return

        sql = "DELETE FROM Airline WHERE airlineName = ?"
        airline_cursor.execute(sql, (airline_name,))
        airline_db.commit()
        airline_db.close()
        await interaction.response.send_message(f"The airline {airline_name}, was deleted.")

    @app_commands.command(name="airline_info", description="Shows info about the airline")
    async def airline_info(self, interaction:discord.Interaction):
        airline_db = sqlite3.connect(db_airline_path)
        airline_cursor = airline_db.cursor()

        sql = "SELECT * FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (interaction.user.id,))
        airline_info = airline_cursor.fetchall()

        if airline_info == []:
            await interaction.response.send_message("You do not own an airline!", ephemeral=True)
            return
        
        general_embed = discord.Embed(color=interaction.user.accent_color, title="General Information")
        general_embed.add_field(name="Airline Name:", value=airline_info[0][1])
        general_embed.add_field(name="ICAO code:", value=airline_info[0][2])
        general_embed.add_field(name="Home Base:", value=airline_info[0][3])
        general_embed.add_field(name="Owner:", value= await self.bot.fetch_user(airline_info[0][4]))
        general_embed.set_footer(text=f"Airline ID is: {airline_info[0][0]}")

        fleet_embed = discord.Embed(color=interaction.user.accent_color, title="Airline fleet")
        fleet_embed.add_field(name="NOT IMPLEMENTED", value="Coming soon")

        hubs_embed = discord.Embed(color=interaction.user.accent_color, title="Airline hubs")
        hubs_embed.add_field(name="NOT IMPLEMENTED", value="Coming soon")

        schedules_embed = discord.Embed(color=interaction.user.accent_color, title="Airline Schedules")
        schedules_embed.add_field(name="NOT IMPLEMENTED", value="Coming soon")

        economy_embed = discord.Embed(color=interaction.user.accent_color, title="Airline Economy")
        economy_embed.add_field(name="NOT IMPLEMENTED", value="Coming soon")
        
        embeds = [general_embed, fleet_embed, hubs_embed, schedules_embed, economy_embed]

        

        class AirlineView(discord.ui.View):         # select 0 = General, select 1 = Fleet, select 2 = hubs, select 3 = schedules, select 4 = Economy
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
                        label = "Fleet",
                        description = "Shows the fleet of the airline",
                        emoji = "✈️"
                    ),
                    discord.SelectOption(
                        label= "Hubs",
                        description = "Shows the hubs of the airline",
                        emoji = "🌐"
                    ),
                    discord.SelectOption(
                        label = "Schedules",
                        description = "Shows the schedules of the airline",
                        emoji = "🎫"
                    ),
                    discord.SelectOption(
                        label = "Economy",
                        description = "Shows economical information of the airline",
                        emoji = "💶"
                    )
                ]
            )
            async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                index = ["General Information", "Fleet", "Hubs", "Schedules", "Economy"].index(select.values[0])
                await interaction.response.edit_message(embed=self.embeds[index], view=self)
        
        await interaction.response.send_message(view=AirlineView(embeds), embed=general_embed)
    
        airline_db.close()

async def setup(bot):
    await bot.add_cog(Airline_Manager(bot))