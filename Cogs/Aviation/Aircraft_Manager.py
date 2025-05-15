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
            sql = f"CREATE TABLE 'Aircraft' (type TEXT, range INTEGER, paxCapacity INTEGER, cargoCapacity INTEGER, motw INTEGER, price INTEGER, cruise_speed INTEGER, airfield_type TEXT, size TEXT)" #if the database doesn't have any table we create it
            cursor.execute(sql)
        db.commit()
        db.close()


    class Aircraft:
        def __init__(self, registration, type, range, pax_capacity, cargo_capacity, motw, price, owner, home_base, cruise_speed, airfield_type, size):
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
            self.size = size

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

        if airline_result == []:
            airline_db.close()
            aircraft_db.close()
            await interaction.followup.send("You do not own an airline", ephemeral=True)
            return
        
        if aircraft_result == []:
            aircraft_db.close()
            airline_db.close()
            await interaction.followup.send(f"The aircraft type {type} does not exist in my database.", ephemeral=True)
            return
        
        if airline_result[0] < aircraft_result[1]:
            aircraft_db.close()
            airline_db.close()
            await interaction.followup.send(f"Your airline does not have enough money to buy this aircraft.", ephemeral=True)
            return
        
        airline_id = airline_result[1]
        new_money = abs(aircraft_result[1] - airline_result[0]) 
        
        class Buttons(discord.ui.View):
            def __init__(self, *, timeout = 180):
                super().__init__(timeout=timeout)

            @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                
                sql = f"INSERT INTO '{airline_id}' (type, registration, hours, location, base) VALUES (?, ?, ?, ?, ?)"
                aircraft_cursor.execute(sql, (type, registration, 0, home_base, home_base))

                sql = "UPDATE Airline SET money = ? WHERE owner = ?"
                airline_cursor.execute(sql, (new_money, interaction.user.id))

                await interaction.response.send_message(f"The aircraft `{registration}` type `{type}` has been purchased, it's waiting for you at `{home_base}!")
                airline_db.commit()
                aircraft_db.commit()
                airline_db.close()
                aircraft_db.close()
                return


            @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                aircraft_db.close()
                aircraft_db.close()
                await interaction.response.send_message(f"Purchase cancelled", ephemeral=True)
                return

        embed = discord.Embed(
            title=f"Purchasing {type}",
            color=0xf1c40f,
            description="Purchase information:"
        )        
        embed.add_field(name="Aircraft type:", value=type)
        embed.add_field(name="Registration:", value=registration)
        embed.add_field(name="Pax capacity:", value="-")
        embed.add_field(name="Cargo capacity:", value="-")
        embed.add_field(name="motw:", value="-")
        embed.add_field(name="Runway type:", value="-")
        embed.add_field(name="Cruise speed:", value="-")
        embed.add_field(name="Home Base:", value=home_base)
        embed.set_footer(text="Plane will be delivered to it's home base")

        await interaction.followup.send(embed=embed, view=Buttons())


async def setup(bot):
    await bot.add_cog(Aircraft_Manager(bot))