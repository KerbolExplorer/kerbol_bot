import discord
from discord import app_commands
from discord.ext import commands
from .Aviation_Utils.Aviation_Utils import airport_lookup, airport_distance, random_flight
import sqlite3
import random
import os

DB_AIRLINE_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airlines.db")
DB_AIRCRAFT_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "aircraft.db")
DB_AIRLINE_MISSIONS_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "missions.db")
DB_AIRPOR_MISSIONS_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airport_missions.db")

class MissionType:
    _id_counter = 0
    def __init__(self, type, departure, arrival, pax, cargo, distance, requires_plane, aircraft_type = None):
        MissionType._id_counter += 1
        self.id = MissionType._id_counter
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

    
    @app_commands.command(name="mission_board", description="Shows the available missions at a given airport")
    @app_commands.describe(airport="ICAO code of the airport you want to check")
    async def mission_board(self, interaction:discord.Interaction, airport:str):
        await interaction.response.defer()
        airport = airport_lookup(airport)
        if not airport:
            await interaction.followup.send("This airport is not in my database.")
            return
        
        mission_types = ("Cargo transport", "Passenger transport", "Ferry flight")
        MAX_MISSIONS = 9

        embed = discord.Embed(
            title=f"Missions for `{airport[0][1]}`",
            color=0xf1c40f
        )

        mission_list = []
        counter = 0

        mission_db = sqlite3.connect(DB_AIRLINE_MISSIONS_PATH)
        missions_cursor = mission_db.cursor()
        sql = f"CREATE TABLE IF NOT EXISTS '{airport[0][1]}' (id INTEGER, type TEXT, departure TEXT, arrival TEXT, pax INTEGER, cargo INTEGER, distance INTEGER, needPlane BOOLEAN, planeType TEXT, reward INTEGER)"
        missions_cursor.execute(sql)

        sql = f"SELECT * FROM '{airport[0][1]}'"
        missions_cursor.execute(sql)
        results = missions_cursor.fetchall()
        if results == []:
            while counter < MAX_MISSIONS:
                flight = random_flight(country=airport[0][8], departing_airport=airport[0][1], min_distance=50, max_distance=300, type="small_airport")
                if not flight:
                    continue

                mission = random.choice(mission_types)
                if mission == "Cargo transport":
                    cargo = random.randint(15, 200)
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
                    plane_type = "C172"
                    mission = MissionType(mission, flight[0], flight[1], 0, 0, distance, True, plane_type)
                    mission_list.append(mission)
                counter += 1

                embed.add_field(name=f"{mission.id}, {mission.type}. `{mission.departure[1]}` - `{mission.arrival[1]}`", value=f"{mission.pax} passengers, {mission.cargo} cargo. {mission.distance}nm. Reward:{mission.reward}")

                sql = f"INSERT INTO '{airport[0][1]}' (id, type, departure, arrival, pax, cargo, distance, needPlane, planeType, reward) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                missions_cursor.execute(sql, (mission.id, mission.type, mission.departure[1], mission.arrival[1], mission.pax, mission.cargo, mission.distance, mission.requires_plane, mission.aircraft_type, mission.reward))
        else:
            for result in results:
                mission = MissionType(result[1], result[2], result[3], result[4], result[5], result[6], result[7])
                embed.add_field(name=f"{mission.id}. {mission.type}. `{mission.departure[1]}` - `{mission.arrival[1]}`", value=f"{mission.pax} passengers, {mission.cargo} cargo. {mission.distance}nm. Reward:{mission.reward}")

        embed.set_footer(text="To accept a mission do S!accept_mission *mission id*")
        
        mission_db.commit()
        mission_db.close()

        await interaction.followup.send(embed=embed)




async def setup(bot):
    await bot.add_cog(Mission_System(bot))