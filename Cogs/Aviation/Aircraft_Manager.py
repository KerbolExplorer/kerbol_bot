import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os

db_airline_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airlines.db")
db_aircraft_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "aircraft.db")

class Aircraft_Manager(commands.Cog):
    def __init__(self, bot):
        self.bot                     # We are making a table for the planes own by every airline. Another table for the store, and another one with default plane data.
    
    class Aircraft:
        def __init__(self, registration, type, range, pax_capacity, cargo_capacity, motw, price, owner, home_base, cruise_speed):
            self.registration = registration
            self.type = type   
            self.range = range
            self.pax_capacity = pax_capacity
            self.cargo_capacity = cargo_capacity
            self.motw = motw
            self.price = price
            self.cruise_speed = cruise_speed
            self.owner = owner
            self.home_base = home_base

async def setup(bot):
    await bot.add_cog(Aircraft_Manager(bot))