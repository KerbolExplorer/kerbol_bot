import discord
from discord import app_commands
from discord.ext import commands
import time
from .Aviation_Utils.Aviation_Utils import airport_lookup, airport_distance, random_flight, registration_creator, get_current_time
import sqlite3
import random
import os

DB_AIRLINE_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airlines.db")
DB_AIRCRAFT_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "aircraft.db")
DB_MISSIONS_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "missions.db")

class MissionType:
    def __init__(self, type, departure, arrival, pax, cargo, distance, requires_plane, aircraft_type = None):
        self.type = type
        self.departure = departure
        self.arrival = arrival
        self.pax = pax
        self.cargo = cargo
        self.requires_plane = requires_plane
        self.aircraft_type = aircraft_type
        self.distance = int(distance)
        self.reward = int(self.calculate_reward())
    def calculate_reward(self):
        if not self.requires_plane:
            reward = self.distance * 75
            return int(reward + 5000)
        else:
            pax_value = 300
            cargo_value = 150
            distance_value = 75
            return int(self.pax * pax_value + self.cargo * cargo_value + distance_value * self.distance)
    
    def __str__(self):
        if self.requires_plane:
            return f"Mission ID: {self.id} {self.type}, from {self.departure[1]} to {self.arrival[1]} ({self.distance}nm) on a {self.aircraft_type}"
        else:
            return f"Mission ID: {self.id} {self.type}, from {self.departure[1]} to {self.arrival[1]} ({self.distance}nm) {self.pax} passengers, {self.cargo} of cargo."

class Mission_System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        db = sqlite3.connect(DB_MISSIONS_PATH)
        cursor = db.cursor()

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='Missions'"
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            sql = "CREATE TABLE IF NOT EXISTS 'Missions' (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, departure TEXT, arrival TEXT, pax INTEGER, cargo INTEGER, distance INTEGER, needPlane BOOLEAN, planeType TEXT, reward INTEGER, airline INTEGER, createdAt INTEGER, planeId INTEGER)"
            cursor.execute(sql)
        
        now = int(time.time())
        MISSION_EXPIRATION = 86400
        expiration_cutoff = now - MISSION_EXPIRATION
        sql = "DELETE FROM Missions WHERE createdAt < ? AND airline = -1"
        cursor.execute(sql, (expiration_cutoff,))
        db.commit()
        db.close()
    
    @app_commands.command(name="mission_board", description="Shows the available missions at a given airport")
    @app_commands.describe(airport="ICAO code of the airport you want to check")
    async def mission_board(self, interaction:discord.Interaction, airport:str):
        await interaction.response.defer()
        airport = airport_lookup(airport)
        if not airport:
            await interaction.followup.send("This airport is not in my database.")
            return
        
        MAX_MISSIONS = 9

        mission_db = sqlite3.connect(DB_MISSIONS_PATH)
        missions_cursor = mission_db.cursor()

        aircraft_db = sqlite3.connect(DB_AIRCRAFT_PATH)
        aircraft_cursor = aircraft_db.cursor()

        sql = "SELECT type FROM Aircraft"
        aircraft_cursor.execute(sql)
        plane_types = aircraft_cursor.fetchall()

        async def generate_missions(airport, country, direction):
            mission_types = ("Cargo transport", "Passenger transport", "Ferry flight\n")
            mission_list = []

            if direction == "From":
                sql = "SELECT * FROM 'Missions' WHERE departure = ?"
            else:
                sql = "SELECT * FROM 'Missions' WHERE arrival = ?"
            missions_cursor.execute(sql, (airport,))
            results = missions_cursor.fetchall()

            number_of_missions = len(results)
            counter = number_of_missions
            MAX_ATTEMPTS = 30
            attempts = 0
            if number_of_missions < MAX_MISSIONS:
                while counter < MAX_MISSIONS and attempts < MAX_ATTEMPTS:
                    attempts += 1
                    if direction == "From":
                        flight = random_flight(country=country, departing_airport=airport, min_distance=50, max_distance=300, type="small_airport")
                    else:
                        flight = random_flight(country=country, arrival_airport=airport, min_distance=50, max_distance=300, type="small_airport")
                    if not flight or flight == 1 or flight == 2 or flight == 3:
                        continue

                    mission = random.choice(mission_types)
                    if mission == "Cargo transport":
                        cargo = random.randint(15, 600)
                        distance = flight[2]
                        mission = MissionType(mission, flight[0], flight[1], 0, cargo, distance, False)
                        mission_list.append(mission)
                    elif mission == "Passenger transport":
                        pax = random.randint(1, 6)
                        distance = flight[2]
                        mission = MissionType(mission, flight[0], flight[1], pax, 0, distance, False)
                        mission_list.append(mission)
                    else:
                        distance = flight[2]
                        plane_type = random.choice(plane_types)[0]
                        mission = MissionType(mission + "-" + plane_type, flight[0], flight[1], 0, 0, distance, True, plane_type)
                        mission_list.append(mission)
                    counter += 1

                    sql = "INSERT INTO 'Missions' (type, departure, arrival, pax, cargo, distance, needPlane, planeType, reward, airline, createdAt, planeId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    missions_cursor.execute(sql, (mission.type, mission.departure[1], mission.arrival[1], mission.pax, mission.cargo, mission.distance, mission.requires_plane, mission.aircraft_type, mission.reward, -1, int(time.time()), -1))
                
                if len(mission_list) == 0:
                    await interaction.response.send_message("Unable to generate any missions for this airport")
                    return

        departure_embed = discord.Embed(
            title=f"Missions from `{airport[0][1]}`",
            color=0xf1c40f
        )

        arrival_embed = discord.Embed(
            title=f"Missions to `{airport[0][1]}`",
            color=0xf1c40f
        )

        await generate_missions(airport[0][1], airport[0][8], "From")
        await generate_missions(airport[0][1], airport[0][8], "To")

        sql = "SELECT id, type, departure, arrival, pax, cargo, distance, reward, airline FROM Missions WHERE departure = ?"
        missions_cursor.execute(sql, (airport[0][1],))
        results = missions_cursor.fetchall()
        for result in results:
            if result[8] == -1:
                departure_embed.add_field(name=f"{result[0]}, {result[1]} `{result[2]}` - `{result[3]}`", value=f"{result[4]} passengers, {result[5]} cargo. {result[6]}nm. Reward:{result[7]}")
            else:
                departure_embed.add_field(name=f"{result[0]}, {result[1]} `{result[2]}` - `{result[3]}` ✈️", value=f"{result[4]} passengers, {result[5]} cargo. {result[6]}nm. Reward:{result[7]}")

        sql = "SELECT id, type, departure, arrival, pax, cargo, distance, reward, airline FROM Missions WHERE arrival = ?"
        missions_cursor.execute(sql, (airport[0][1],))
        results = missions_cursor.fetchall()
        for result in results:
            if result[8] == -1:
                arrival_embed.add_field(name=f"{result[0]}, {result[1]} `{result[2]}` - `{result[3]}`", value=f"{result[4]} passengers, {result[5]} cargo. {result[6]}nm. Reward:{result[7]}")
            else:
                arrival_embed.add_field(name=f"{result[0]}, {result[1]} `{result[2]}` - `{result[3]}` ✈️", value=f"{result[4]} passengers, {result[5]} cargo. {result[6]}nm. Reward:{result[7]}")

        arrival_embed.set_footer(text="To accept a mission do S!mission *mission id*. A ✈️ besides a mission means that someone has already accepted it.")   
        departure_embed.set_footer(text="To accept a mission do S!mission *mission id*. A ✈️ besides a mission means that someone has already accepted it.")
        mission_db.commit()
        mission_db.close()
        aircraft_db.close()

        embeds = (departure_embed, arrival_embed)

        class MissionView(discord.ui.View):
            def __init__(self, embeds):
                super().__init__()
                self.embeds = embeds
            
            @discord.ui.select(
                placeholder="Select an option:",
                min_values= 1,
                max_values= 1,
                options = [
                    discord.SelectOption(
                        label="From",
                        description ="Shows the missions from this airport",
                        emoji ="↗️"
                    ),
                    discord.SelectOption(
                        label = "To",
                        description = "Shows the missions to this airport",
                        emoji = "↘️"
                    )
                ]
            )
            async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                index = ["From", "To"].index(select.values[0])
                await interaction.response.edit_message(embed=self.embeds[index], view=self)

        await interaction.followup.send(view=MissionView(embeds), embed=departure_embed)
    
    @commands.command()
    async def mission(self, ctx, mission:int):
        author = ctx.author.id
        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()
        sql = "SELECT airlineId FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (author,))
        airline_result = airline_cursor.fetchone()

        if airline_result is None:
            await ctx.send("You do not own an airline!")
            airline_db.close()
            return

        mission_db = sqlite3.connect(DB_MISSIONS_PATH)
        mission_cursor = mission_db.cursor()
        sql = "SELECT * FROM Missions WHERE id = ?"
        mission_cursor.execute(sql, (mission,))
        result = mission_cursor.fetchone()

        if result is None:
            await ctx.send("No missions exists with this id!")
            airline_db.close()
            mission_db.close()
            return
        
        if result[7]:
            embed = discord.Embed(
            title=f"{result[1]} from `{result[2]}` to `{result[3]}` ({result[6]})",
            description='Ferry flights will add the plane to your airline with the "rented" condition. You are free to do with them as you please as long as they arrive at their destination in 24 hours. If you fail to deliver the plane on time a penalty will be substracted from your reward based on the distance. It can hit the negatives',
            color=0xf1c40f
            )
            embed.add_field(name="Aircraft:", value=result[8])
            embed.add_field(name="Reward:", value=result[9])
            embed.add_field(name="Late Penalty:", value="100 per nm")
        else:    
            embed = discord.Embed(
            title=f"{result[1]} from `{result[2]}` to `{result[3]}`",
            description="Cargo/Pax can be hauled in several flights if it doesn't fit on the plane in one go",
            color=0xf1c40f
            )
            embed.add_field(name="Passengers:", value=result[4])
            embed.add_field(name="Cargo:", value=result[5])
            embed.add_field(name="Reward:", value=result[9])

        embed.set_footer(text="You can cancel a mission with S!mission_cancel id")


        class Buttons(discord.ui.View):
            def __init__(self, *, timeout = 180):
                super().__init__(timeout=timeout)
            @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
            async def confirmed(self, interaction:discord.Interaction, button:discord.ui.Button):
                if result[7]:
                    destination = airport_lookup(result[3])
                    registration = registration_creator(iso_code=destination[0][8])
                    sql = "INSERT INTO AircraftList (airlineId, type, registration, hours, currentPax, currentCargo, location, homeBase, status, engineStatus, isRented, returnAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    aircraft_db = sqlite3.connect(DB_AIRCRAFT_PATH)
                    aircraft_cursor = aircraft_db.cursor()
                    aircraft_cursor.execute(sql, (airline_result[0], result[8], registration, 0, 0, 0, result[2], result[3], 100, 100, True, get_current_time() + 86400))
                    sql = "SELECT id FROM AircraftList WHERE registration = ? AND airlineId = ? AND type = ? and location = ? AND isRented = 1" # If this ever bugs I'm kms
                    aircraft_cursor.execute(sql, (registration, airline_result[0], result[8], result[2]))
                    aircraft_id = aircraft_cursor.fetchone()[0]
                    aircraft_db.commit()
                    aircraft_db.close()
                    sql = "UPDATE Missions SET planeId = ?, airline = ? WHERE id = ?"
                    mission_cursor.execute(sql, (aircraft_id, airline_result[0], mission))
                    await interaction.response.send_message(f"You have accepted the mission, the aircraft is waiting for you at {result[2]}, you have 24 hours to deliver it. Good luck!", ephemeral=True)
                else:
                    sql = "UPDATE Missions SET airline = ? WHERE id = ?"
                    mission_cursor.execute(sql, (airline_result[0], mission))
                    await interaction.response.send_message("You have accepted the mission, good luck!", ephemeral=True)
                mission_db.commit()
                mission_db.close()
                airline_db.close()
                return

            @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                mission_db.close()
                airline_db.close()
                await interaction.response.send_message("You have not accepted the mission.", ephemeral=True)
                return


        await ctx.send(view=Buttons(), embed=embed)   

    @commands.command()
    async def mission_complete(self, ctx, mission:int):
        author = ctx.author.id
        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()
        sql = "SELECT airlineId, money FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (author,))
        airline_result = airline_cursor.fetchone()

        if airline_result is None:
            await ctx.send("You do not own an airline!")
            airline_db.close()
            return
        
        mission_db = sqlite3.connect(DB_MISSIONS_PATH)
        mission_cursor = mission_db.cursor()
        sql = "SELECT id, airline, reward FROM Missions WHERE id = ?"
        mission_cursor.execute(sql, (mission,))
        result = mission_cursor.fetchone()

        if result[1] != airline_result[0]:
            await ctx.send("You have not accepted this mission!")
            airline_db.close()
            mission_db.close()
            return
        
        if result is None:
            await ctx.send("No missions exists with this id!")
            airline_db.close()
            mission_db.close()
            return
        
        new_total = airline_result[1] + result[2]

        sql = "UPDATE Airline SET money = ? WHERE airlineId = ?"
        airline_cursor.execute(sql, (new_total, airline_result[0]))

        sql = "DELETE FROM Missions WHERE id = ?"
        mission_cursor.execute(sql, (result[0],))

        await ctx.send("The mission has been completed and the reward has been added to your account")
        airline_db.commit()
        mission_db.commit()
        airline_db.close()
        mission_db.close()

    @commands.command()
    async def mission_cancel(self, ctx, mission:int):  
        author = ctx.author.id
        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()
        sql = "SELECT airlineId FROM Airline WHERE owner = ?"
        airline_cursor.execute(sql, (author,))
        airline_result = airline_cursor.fetchone()

        if airline_result is None:
            await ctx.send("You do not own an airline!")
            airline_db.close()
            return
        
        mission_db = sqlite3.connect(DB_MISSIONS_PATH)
        mission_cursor = mission_db.cursor()
        sql = "SELECT id, airline, planeId FROM Missions WHERE id = ?"
        mission_cursor.execute(sql, (mission,))
        result = mission_cursor.fetchone()

        if result[1] != airline_result[0]:
            await ctx.send("You have not accepted this mission!")
            airline_db.close()
            mission_db.close()
            return
        
        if result is None:
            await ctx.send("No missions exists with this id!")
            airline_db.close()
            mission_db.close()
            return
           
        if result[2] != -1:
            sql = "DELETE FROM AircraftList WHERE id = ?"
            aircraft_db = sqlite3.connect(DB_AIRCRAFT_PATH)
            aircraft_db.cursor().execute(sql, (result[2],))
            aircraft_db.commit()
            aircraft_db.close()
        
        sql = "UPDATE Missions SET airline = -1, planeId = -1 WHERE id = ?"
        mission_cursor.execute(sql, (mission,))
        mission_db.commit()
        mission_db.close()
        airline_db.close()
        await ctx.message.add_reaction("✅")
    


async def setup(bot):
    await bot.add_cog(Mission_System(bot))