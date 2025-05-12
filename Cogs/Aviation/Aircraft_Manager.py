import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os

DB_AIRLINE_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airlines.db")
DB_AIRCRAFT_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "aircraft.db")

class Aircraft_Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # We are making a table for the planes own by every airline. Another table for the store, and another one with default plane data.

        db = sqlite3.connect(DB_AIRCRAFT_PATH)
        cursor = db.cursor()
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='Aircraft'" #check if the database has a table
        cursor.execute(sql)
        result = cursor.fetchall()  
        if not result:
            sql = f"CREATE TABLE 'Aircraft' (type TEXT, range INTEGER, paxCapacity INTEGER, cargoCapacity INTEGER, motw INTEGER, price INTEGER, cruise_speed INTEGER, airfield_type TEXT)" #if the database doesn't have any table we create it
            cursor.execute(sql)
        db.commit()
        db.close


    class Aircraft:
        def __init__(self, registration, type, range, pax_capacity, cargo_capacity, motw, price, owner, home_base, cruise_speed, airfield_type):
            self.registration = registration
            self.type = type   
            self.range = range
            self.pax_capacity = pax_capacity
            self.cargo_capacity = cargo_capacity
            self.motw = motw
            self.price = price
            self.cruise_speed = cruise_speed
            self.airfield_type = airfield_type
            self.owner = owner
            self.home_base = home_base


async def setup(bot):
    await bot.add_cog(Aircraft_Manager(bot))