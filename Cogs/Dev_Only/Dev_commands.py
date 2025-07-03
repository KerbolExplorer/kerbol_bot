import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import sqlite3
from dotenv import load_dotenv
load_dotenv()

ADMIN = os.getenv("ADMIN")

DB_AIRPORT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Aviation", "Aviation_Databases", "airports.db"))

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
    
    #This command will update databases as required
    @commands.command()
    async def update(self, ctx):
        try:
            user_id = ctx.author.id
            if self.verify_messenger(user_id) == True:
                db = sqlite3.connect("db_exp.db")
                cursor = db.cursor()

                sql = "UPDATE '606456281469026305' SET cooldownEnd = 0 WHERE userId = 442728041115025410"
                cursor.execute(sql)
                db.commit()
                db.close()
                await ctx.message.add_reaction("✅")
            else:
                return
        except Exception as e:
            print(e)


    # S!add_airport KAVX small_airport "Catalina Airport" 33.404 -118.414878 1541 NA US Avalon US-CA no
    @commands.command()
    async def add_airport(self, ctx, ident, type, name, latitude, longitude, elevation:int, continent, country, location, region, scheduled_service):
        if self.verify_messenger(ctx.author.id) == True:
            db = sqlite3.connect(DB_AIRPORT_PATH)
            cursor = db.cursor()
            sql = "INSERT INTO airports (ident, type, name, latitude_deg, longitude_deg, elevation_ft, continent, iso_country, municipality, iso_region, scheduled_service) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(sql, (ident, type, name, latitude, longitude, elevation, continent, country, location, region, scheduled_service))
            await ctx.message.add_reaction("✅")
            db.commit()
            db.close()
        else:
            await ctx.message.add_reaction("❌")

        #S!edit_airport KVAX KAVX small_airport "Catalina Airport" 33.404 -118.414878 1541 NA US Avalon US-CA no
    @commands.command()
    async def edit_airport(self, ctx, ident, new_ident, type, name, latitude, longitude, elevation:int, continent, country, location, region, scheduled_service):
        try:
            if self.verify_messenger(ctx.author.id) == True:
                db = sqlite3.connect(DB_AIRPORT_PATH)
                cursor = db.cursor()
                sql = "UPDATE airports SET ident = ?, type = ?, name = ?, latitude_deg = ?, longitude_deg = ?, elevation_ft = ?, continent = ?, iso_country = ?, municipality = ?, iso_region = ?, scheduled_service = ? WHERE ident = ?"
                cursor.execute(sql, (new_ident, type, name, latitude, longitude, elevation, continent, country, location, region, scheduled_service, ident))
                await ctx.message.add_reaction("✅")
                db.commit()
                db.close()
            else:
                await ctx.message.add_reaction("❌")    
        except Exception as e:
            print(e)    

                

async def setup(bot):
    await bot.add_cog(Dev_commands(bot))