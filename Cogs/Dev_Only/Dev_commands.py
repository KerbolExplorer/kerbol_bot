import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

ADMIN = os.getenv("ADMIN")
DB_AIRCRAFT_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "aircraft.db")

class Dev_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def verify_messenger(self, id):
        if int(id) != int(ADMIN):
            return False
        else:
            return True

    # Like the ping command but even more barebones
    @commands.command()
    async def test(self, ctx):
        user_id = ctx.author.id
        if self.verify_messenger(user_id) == True:
            await ctx.send("This works")
        else:
            return
    
    # Unloads the responses cog to make the bot shut up when responded.
    @commands.command()
    async def shutup(self, ctx, time: int = 60):
        user_id = ctx.author.id
        if self.verify_messenger(user_id) == True:
            await self.bot.unload_extension("Cogs.Misc.Responses")
            await ctx.message.add_reaction("✅")
            await asyncio.sleep(time)
            await self.bot.load_extension("Cogs.Misc.Responses")
        else:
            await ctx.send("And who do you think you are to tell me that?!")

    # Unloads the cog with the specified path. 
    @commands.command()
    async def unload(self, ctx, cog: str, time: int = 60):
        user_id = ctx.author.id
        if self.verify_messenger(user_id) == True:
            if cog is None:
                await ctx.send("Please send the path of the cog you want to unload")
                await ctx.message.add_reaction("❌")
                return
            elif cog == "Cogs.Dev_Only.Dev_commands":
                await ctx.send("This cog can not be disabled.")
                await ctx.message.add_reaction("❌")
                return
            else:
                await self.bot.unload_extension(cog)
                await ctx.message.add_reaction("✅")
                await asyncio.sleep(time)
                await self.bot.load_extension(cog)
                await ctx.author.send(f"The cog with the path `{cog}` has been re-enabled after a manual shutdown.")
                return
        else:
            return
        
    @commands.command()
    async def add_aircraft(self, ctx, type:str, range:int, pax_capacity:int, cargo_capacity:int, motw:int, price:int, cruise_speed:int, airfield_type:str):
        print("Command triggered!")
        if self.verify_messenger(ctx.author.id) == True:
            db = sqlite3.connect(DB_AIRCRAFT_PATH)
            cursor = db.cursor()
            sql = f"INSERT INTO Aircraft (type, range, paxCapacity, cargoCapacity, motw, price, cruise_speed, airfield_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(sql, (type, range, pax_capacity, cargo_capacity, motw, price, cruise_speed, airfield_type))
            await ctx.message.add_reaction("✅")
            db.commit()
            db.close()
        else:
            await ctx.message.add_reaction("❌")
                

async def setup(bot):
    await bot.add_cog(Dev_commands(bot))