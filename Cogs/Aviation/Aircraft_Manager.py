import discord
from discord import app_commands
from discord.ext import commands
from .Aviation_Utils.Aviation_Utils import airport_lookup
import sqlite3
import os

DB_AIRLINE_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airlines.db")
DB_AIRCRAFT_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "aircraft.db")
DB_MISSIONS_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "missions.db")

class Aircraft_Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # We are making a table for the planes own by every airline. Another table for the store, and another one with default plane data.

        db = sqlite3.connect(DB_AIRCRAFT_PATH)
        cursor = db.cursor()
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='Aircraft'" #check if plane template table exists
        cursor.execute(sql)
        result = cursor.fetchall()  
        if not result:
            sql = "CREATE TABLE 'Aircraft' (type TEXT, range INTEGER, paxCapacity INTEGER, cargoCapacity INTEGER, motw INTEGER, empty INTEGER, price INTEGER, cruise_speed INTEGER, airfield_type TEXT, size TEXT)" #if the database doesn't have any table we create it
            cursor.execute(sql)

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='AircraftList'"
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            sql = "CREATE TABLE 'AircraftList' (id INTEGER PRIMARY KEY AUTOINCREMENT, airlineId INTEGER, type TEXT, registration TEXT, hours TEXT, currentPax INTEGER, currentCargo INTEGER, location TEXT, homeBase TEXT, status INTEGER, engineStatus INTEGER)"
            cursor.execute(sql)
        
        db.commit()
        db.close()

    @app_commands.command(name="buy-aircraft", description="Buy a brand new aircraft for your airline")
    @app_commands.describe(
        type="The type of the aircraft (C172, B738, A320..)",
        registration="The registration of the aircraft",
        home_base="The home base of the aircraft. It will be delivered here."
        )
    async def buy_aircraft(self, interaction:discord.Interaction, type:str, registration:str, home_base:str):
        await interaction.response.defer()
        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()
        aircraft_db = sqlite3.connect(DB_AIRCRAFT_PATH)
        aircraft_cursor = aircraft_db.cursor()


        sql = "SELECT money, airlineId FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (interaction.user.id,))
        airline_result = airline_cursor.fetchone()

        sql = "SELECT type, price FROM Aircraft WHERE type = ?"
        aircraft_cursor.execute(sql, (type,))
        aircraft_result = aircraft_cursor.fetchone()

        if airline_result == None:
            airline_db.close()
            aircraft_db.close()
            await interaction.followup.send("You do not own an airline", ephemeral=True)
            return
        
        if aircraft_result == None:
            aircraft_db.close()
            airline_db.close()
            await interaction.followup.send(f"The aircraft type `{type}` does not exist in my database.", ephemeral=True)
            return

        if airline_result[0] < aircraft_result[1]:
            aircraft_db.close()
            airline_db.close()
            await interaction.followup.send(f"Your airline does not have enough money to buy this aircraft.", ephemeral=True)
            return
        
        if airport_lookup(home_base) == False:
            await interaction.followup.send(f"Airport `{home_base}` does not exist in my database.")
            return
        
        airline_id = airline_result[1]
        new_money = abs(aircraft_result[1] - airline_result[0]) 
        
        class Buttons(discord.ui.View):
            def __init__(self, *, timeout = 180):
                super().__init__(timeout=timeout)

            @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                
                sql = f"INSERT INTO AircraftList (airlineId, type, registration, hours, currentPax, currentCargo, location, homeBase, status, engineStatus) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                aircraft_cursor.execute(sql, (airline_id, type, registration, 0, 0, 0, home_base, home_base, 100, 100))

                sql = "UPDATE Airline SET money = ? WHERE owner = ?"
                airline_cursor.execute(sql, (new_money, interaction.user.id))

                await interaction.response.send_message(f"The aircraft `{registration}` type `{type}` has been purchased, it's waiting for you at `{home_base}`!")
                airline_db.commit()
                aircraft_db.commit()
                airline_db.close()
                aircraft_db.close()
                return


            @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                aircraft_db.close()
                airline_db.close()
                await interaction.response.send_message(f"Purchase cancelled", ephemeral=True)
                return

        embed = discord.Embed(
            title=f"Purchasing {type}",
            color=0xf1c40f,
            description="Purchase information:"
        )        
        sql = "SELECT * FROM Aircraft WHERE type = ?"
        aircraft_cursor.execute(sql, (type,))
        result = aircraft_cursor.fetchone()
        embed.add_field(name="Aircraft type:", value=type)
        embed.add_field(name="Registration:", value=registration)
        embed.add_field(name="Range:", value=result[1])
        embed.add_field(name="Pax capacity:", value=result[2])
        embed.add_field(name="Cargo capacity:", value=result[3])
        embed.add_field(name="motw:", value=str(result[4]) + "kg")
        embed.add_field(name="Empty:", value=str(result[5]) + "kg")
        embed.add_field(name="Runway type:", value=result[6])
        embed.add_field(name="Cruise speed:", value=result[7])
        embed.add_field(name="Home Base:", value=home_base)
        embed.add_field(name="Price:", value=result[8])
        embed.set_footer(text="Plane will be delivered to it's home base")

        await interaction.followup.send(embed=embed, view=Buttons())
    
    @app_commands.command(name="load-aircraft", description="Loads an aircraft with a mission's cargo")
    @app_commands.describe(
        aircraft="The registration of the plane",
        mission_id="The id of the mission to load"
    )
    async def load_aircraft(self, interaction:discord.Interaction, aircraft:str, mission_id:int):  #This allows you to load the aircraft with cargo, you should also be allowed to partially load cargo
        await interaction.response.defer(ephemeral=True)

        mission_db = sqlite3.connect(DB_MISSIONS_PATH)
        missions_cursor = mission_db.cursor()

        sql = "SELECT departure, pax, cargo, needPlane, airline, planeId FROM Missions WHERE id = ?"

        missions_cursor.execute(sql, (mission_id,))
        mission_data = missions_cursor.fetchone()   #0 = departure, 1 = pax, 2 = cargo, 3 = needPlane, 4 = airline, 5 = planeId

        if mission_data == None:
            await interaction.followup.send("This mission does not exist.")
            missions_cursor.close()
            mission_db.close()  
            return
        elif mission_data[3] == True:
            await interaction.followup.send("This mission cannot be loaded on a plane.")
            missions_cursor.close()
            mission_db.close()  
            return
        elif mission_data[5] != -1:
            await interaction.followup.send("This mission has already been loaded on another plane")
            missions_cursor.close()
            mission_db.close()  
            return

        aircraft_db = sqlite3.connect(DB_AIRCRAFT_PATH)
        aircraft_cursor = aircraft_db.cursor()

        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()

        owner = interaction.user.id

        sql = "SELECT airlineId FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (owner,))
        airline_id = airline_cursor.fetchone()[0]

        if airline_id != mission_data[4]:
            await interaction.followup.send("You did not accept this mission.")
            missions_cursor.close()
            mission_db.close()
            airline_cursor.close()
            airline_db.close()
            aircraft_cursor.close()
            aircraft_db.close()
            return

        airline_cursor.close()
        airline_db.close()

        sql = "SELECT id, type, location, currentPax, currentCargo, registration FROM AircraftList WHERE airlineId = ? AND registration = ?"
        aircraft_cursor.execute(sql, (airline_id, aircraft))
        aircraft = aircraft_cursor.fetchone()       # 0 = id, 1 = type 2 = location, 3 = currentpax, 4 = currentCargo, 5 = registration

        if aircraft == None:
            await interaction.followup.send("You have no aircraft with that registration")
            missions_cursor.close()
            mission_db.close()
            aircraft_cursor.close()
            aircraft_db.close()
            return     

        if aircraft[2] != mission_data[0]:
            await interaction.followup.send(f"This aircraft `{aircraft[2]}` is not at the same airport as the mission departure `{mission_data[0]}`")
            missions_cursor.close()
            mission_db.close()
            aircraft_cursor.close()
            aircraft_db.close()
            return

        sql = "SELECT type, paxCapacity, cargoCapacity, motw, empty FROM Aircraft WHERE type = ?"
        aircraft_cursor.execute(sql, (aircraft[1],))
        aircraft_data = aircraft_cursor.fetchone()  #0 = type, 1 = paxCapacity, 2 = cargoCapacity, 3 = motw, 4 = empty

        # Check if this won't exceed the capacity of the plane
        new_pax = aircraft[3] + mission_data[1]
        new_cargo = aircraft[4] +  mission_data[2]

        if new_pax > aircraft_data[1] or new_cargo > aircraft_data[2]:
            await interaction.followup.send("⚠️The pax/cargo for this mission doesn't fit in this aircraft")
            missions_cursor.close()
            mission_db.close()
            aircraft_cursor.close()
            aircraft_db.close()
            return
        elif (new_pax * 80) + new_cargo + aircraft_data[4] > aircraft_data[3]:
            await interaction.followup.send("⚠️Can't load pax/cargo, motw exceeded") 
            missions_cursor.close()
            mission_db.close()
            aircraft_cursor.close()
            aircraft_db.close()
            return
        
        sql = "UPDATE AircraftList SET currentPax = ?, currentCargo = ? WHERE id = ?"
        aircraft_cursor.execute(sql, (new_pax, new_cargo, aircraft[0]))

        sql = "UPDATE Missions SET planeId = ? WHERE id = ?"
        missions_cursor.execute(sql, (aircraft[0], mission_id))

        aircraft_db.commit()
        aircraft_cursor.close()
        aircraft_db.close()

        mission_db.commit()
        missions_cursor.close()
        mission_db.close()

        await interaction.followup.send(f"`{aircraft[5]}` has been loaded with the mission's cargo. You can check it's data on the aircraft's menu with `/aircraft *registration*`")

    @app_commands.command(name="unload-aircraft", description="Unloads a mission from an aircraft")
    @app_commands.describe(
        aircraft="The registration of the plane",
        mission_id="The id of the mission to unload"
    )
    async def unload_aircraft(self, interaction:discord.Interaction, aircraft:str, mission_id:int):
        await interaction.response.defer(ephemeral=True)

        mission_db = sqlite3.connect(DB_MISSIONS_PATH)
        missions_cursor = mission_db.cursor()

        sql = "SELECT arrival, pax, cargo, needPlane, airline, planeId, reward FROM Missions WHERE id = ?"

        missions_cursor.execute(sql, (mission_id,))
        mission_data = missions_cursor.fetchone()   #0 = departure, 1 = pax, 2 = cargo, 3 = needPlane, 4 = airline, 5 = planeId, 6 = reward

        if mission_data == None:
            await interaction.followup.send("This mission does not exist.")
            missions_cursor.close()
            mission_db.close()            
            return
        elif mission_data[5] == -1:
            await interaction.followup.send("This mission has not been loaded on any aircraft")
            missions_cursor.close()
            mission_db.close()
            return

        aircraft_db = sqlite3.connect(DB_AIRCRAFT_PATH)
        aircraft_cursor = aircraft_db.cursor()

        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()

        owner = interaction.user.id

        sql = "SELECT airlineId, money FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (owner,))
        result = airline_cursor.fetchone()

        airline_id = result[0]

        if airline_id != mission_data[4]:
            await interaction.followup.send("You did not accept this mission.")

            missions_cursor.close()
            mission_db.close()
            airline_cursor.close()
            airline_db.close()
            aircraft_cursor.close()
            aircraft_db.close()
            return

        sql = "SELECT id, type, location, currentPax, currentCargo, registration FROM AircraftList WHERE airlineId = ? AND registration = ?"
        aircraft_cursor.execute(sql, (airline_id, aircraft))
        aircraft = aircraft_cursor.fetchone()       # 0 = id, 1 = type 2 = location, 3 = currentpax, 4 = currentCargo, 5 = registration

        if aircraft == None:
            await interaction.followup.send("You have no aircraft with that registration")
            missions_cursor.close()
            mission_db.close()
            airline_cursor.close()
            airline_db.close()
            aircraft_cursor.close()
            aircraft_db.close()
            return     

        new_cargo = aircraft[4] -  mission_data[2]
        new_pax = aircraft[3] - mission_data[1]
        sql = "UPDATE AircraftList SET currentPax = ?, currentCargo = ? WHERE id = ?"
        aircraft_cursor.execute(sql, (new_pax, new_cargo, aircraft[0]))

        sql = "UPDATE Missions SET planeId = ?, airline = ? WHERE id = ?"
        missions_cursor.execute(sql, (-1, -1, mission_id))

        #if the aircraft is at the same airport as the destination of the mission, it's a mission complete
        if aircraft[2] == mission_data[0]:
            sql = "UPDATE Airline SET money = ? WHERE airlineId = ?"
            new_total = result[1] + mission_data[6]
            airline_cursor.execute(sql, (new_total, airline_id))
            
            sql = "DELETE FROM Missions WHERE id = ?"
            missions_cursor.execute(sql, (mission_id,))
            await interaction.followup.send("The mission has been marked as completed and the reward has been added to your account")
        else:
            await interaction.followup.send("The mission has been sucessfully unloaded from the aircraft")

        aircraft_db.commit()
        aircraft_cursor.close()
        aircraft_db.close()

        mission_db.commit()
        missions_cursor.close()
        mission_db.close()

        airline_db.commit()
        airline_cursor.close()
        airline_db.close()


    @app_commands.command(name="aircraft-info", description="Shows information about an owned plane")
    @app_commands.describe(aircraft="The registration of the aircraft")
    async def aircraft_info(self, interaction:discord.Interaction, aircraft:str):
        await interaction.response.send_message("Not implemented")

    @app_commands.command(name="move-aircraft", description="Moves an aircraft from one airport to the other")
    @app_commands.describe(aircraft="Registration of the aircraft", destination="Icao code of the destination")
    async def move_aircraft(self, interaction:discord.Interaction, aircraft:str, destination:str):
        await interaction.response.defer(ephemeral=True)
        destination = destination.upper()

        if airport_lookup(destination) == False:
            await interaction.followup.send(f"The airport {destination} is not in my database.")
            return

        aircraft_db = sqlite3.connect(DB_AIRCRAFT_PATH)
        aircraft_cursor = aircraft_db.cursor()

        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()

        sql = "SELECT airlineId FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (interaction.user.id,))
        airline_id = airline_cursor.fetchone()[0]

        sql = "SELECT id FROM AircraftList WHERE registration = ? AND airlineId = ?"
        aircraft_cursor.execute(sql, (aircraft, airline_id))
        aircraft_id = aircraft_cursor.fetchone()

        if aircraft_id == None:
            await interaction.followup.send(f"You do not own any aircraft registered as {aircraft}")
            return
        
        aircraft_id = aircraft_id[0]

        airline_cursor.close()
        airline_db.close()
        sql = "UPDATE AircraftList SET location = ? WHERE id = ?"

        aircraft_cursor.execute(sql, (destination, aircraft_id))

        aircraft_db.commit()
        aircraft_cursor.close()
        aircraft_db.close()

        await interaction.followup.send(f"Aircraft `{aircraft}` has been moved to `{destination}`")

async def setup(bot):
    await bot.add_cog(Aircraft_Manager(bot))