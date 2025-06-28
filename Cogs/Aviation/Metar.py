import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timezone
import asyncio
import sqlite3
import os
from .Aviation_Utils.Aviation_Utils import get_metar, get_current_zulu
from .Aviation_Utils.Aviation_Math import hpa_to_inhg, inhg_to_hpa

db_requests_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "requests.db")

class Metar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not self.send_metar.is_running():
            self.send_metar.start()

        request_db = sqlite3.connect(db_requests_path)
        request_cursor = request_db.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='Requests'"
        request_cursor.execute(sql)
        result = request_cursor.fetchall()
        if not result:
            sql = "CREATE TABLE 'Requests' (userId INTEGER, airportICAO TEXT, calls INTEGER, nextCall INTEGER)"
            request_cursor.execute(sql)
        request_db.commit()
        request_db.close()

    def get_metar_embed(self, metar):
            # Getting the proper zulu time
            zulu_time = datetime.fromtimestamp(metar['obsTime'], tz=timezone.utc)
            zulu_time = zulu_time.strftime("%H%MZ")

            # Handles how the wind is displayed, depending on gusts or vrb winds
            if metar['wgst'] is not None:
                wind = f"From {metar['wdir']}º at {metar['wspd']}kt, gusting at {metar['wgst']}kt\n"
            elif metar['wdir'] == "VRB":
                wind = f"Variable winds at {metar['wspd']}kt\n"
            else:
                wind = f"From {metar['wdir']}º at {metar['wspd']}kt\n"
            
            # Cloud cover handling
            clouds = ""
            if metar['clouds'][0]['cover'] == 'CAVOK' or metar['clouds'][0]['cover'] == 'CLR':
                clouds = "Clear skies"
            else:
                cover_types = {
                    'FEW' : 'Few clouds', 
                    'SCT' : 'Scattered clouds', 
                    'BKN' : 'Broken clouds', 
                    'OVC' : 'Overcast clouds', 
                    'CB' : 'Cumulonimbus clouds', 
                    'TCU' : 'Towering cumulus clouds',
                    'OVX' : 'Overcast Sky'
                               }
                for layer in metar['clouds']:
                    try:
                        clouds += f"{cover_types[layer['cover']]} at {layer['base']}ft. "
                    except KeyError:
                        clouds = f"⚠️Could not match cloud type {layer['cover']}"
                        break

            embed = discord.Embed(
                title=f"METAR: `{metar['icaoId']}`",
                description=f"**Raw Report**\n```{metar['rawOb']}```",
                color=discord.Color.blue()
            )
            embed.add_field(name="**Data Summary**", value=(
                f"**Station** : {metar['icaoId']} ({metar['name']})\n"
                f"**Observed at** : {zulu_time}\n"
                f"**Wind** : {wind}"
                f"**Visibility** : {metar['visib']}km\n"
                f"**Temperature** : {metar['temp']}ºC\n"
                f"**Dew Point** : {metar['dewp']}ºC\n"
                f"**Altimeter** : {int(metar['altim'])}hpa ({hpa_to_inhg(float(metar['altim']))}inhg)\n"
                f"**Clouds**: {clouds}"
            ), inline=False)
            embed.set_footer(text="For flight simulation use only. Source: https://aviationweather.gov/api/data/metar")
            return embed
    
    def get_time(self):
        return int(datetime.now(timezone.utc).timestamp())

    @app_commands.command(name="metar", description="Gets the metar for an airport")
    @app_commands.describe(airport="Icao code of the airport")
    async def metar(self, interaction:discord.Interaction, airport:str):
        await interaction.response.defer()
        metar = get_metar(airport, False)

        if metar == False:
            await interaction.followup.send("There was an issue getting this metar.", ephemeral=True)
        elif metar == None:
            await interaction.followup.send("This metar is not available.", ephemeral=True)
        else:
            embed = self.get_metar_embed(metar)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="metar_request", description="Have Solgaleo periodically send you the metar for an airport")
    @app_commands.describe(
        airport="Icao code of the airport",
        hours="How many hours you want to be reminded for"
    )
    async def metar_request(self, interaction:discord.Interaction, airport:str, hours:int):
        await interaction.response.defer(ephemeral=True)
        metar = get_metar(airport, False)

        if metar == False:
            await interaction.followup.send("There was an issue getting this metar.")
        elif metar == None:
            await interaction.followup.send("This metar is not available.")
        else:
            request_db = sqlite3.connect(db_requests_path)
            request_cursor = request_db.cursor()
            sql = "SELECT * FROM Requests WHERE userId = ? AND airportICAO = ?"
            request_cursor.execute(sql, (interaction.user.id, airport.upper()))
            result = request_cursor.fetchall()

            next_call = self.get_time()
            next_call += 3600
            if result == []:
                sql = "INSERT INTO Requests (userId, airportICAO, calls, nextCall) VALUES (?, ?, ?, ?)"
                request_cursor.execute(sql, (interaction.user.id, airport.upper(), hours, next_call))
            else:
                await interaction.followup.send(f"You already have a request for `{airport.upper()}`!")
                request_db.close()
                return
            request_db.commit()
            request_db.close()

            await interaction.followup.send(f"Roger that, I'll DM you the metar of `{airport.upper()}` during {hours} hours. If you wish to cancel, do `/metar_stop`")

    @app_commands.command(name="metar_stop", description="Cancels a metar request or all of them")
    @app_commands.describe(
        airport="The airport you want to cancel the request for, leave empty if you wish to cancel all the requests"
    )
    async def metar_stop(self, interaction:discord.Interaction, airport:str = None):
        request_db = sqlite3.connect(db_requests_path)
        request_cursor = request_db.cursor()

        #Check if the user has any metar requests
        sql = "SELECT * FROM Requests WHERE userId = ?"
        request_cursor.execute(sql, (interaction.user.id,))
        result = request_cursor.fetchall()
        if result == []:
            await interaction.response.send_message("You don't have any metar requests", ephemeral=True)
        else:
            if airport == None:
                sql = "DELETE FROM Requests WHERE userId = ?"
                request_cursor.execute(sql, (interaction.user.id,))
                await interaction.response.send_message("All of your metar requests have been cancelled", ephemeral=True)
            else:
                sql = "SELECT * FROM Requests WHERE userId = ? AND airportICAO = ?"
                request_cursor.execute(sql, (interaction.user.id, airport.upper()))
                result = request_cursor.fetchall()
                if result == []:
                    await interaction.response.send_message(f"I Couldn't find any metar requests for `{airport.upper()}`", ephemeral=True)
                else:
                    sql= "DELETE FROM Requests WHERE userId = ? AND airportICAO = ?"
                    request_cursor.execute(sql, (interaction.user.id, airport.upper()))
                    await interaction.response.send_message(f"Alright, I've cancelled the metar requests for `{airport.upper()}`", ephemeral=True)

        request_db.commit()
        request_db.close()

    @app_commands.command(name="metar_list", description="Returns a list of the metars you requested")
    async def metar_list(self, interaction:discord.Interaction):
        request_db = sqlite3.connect(db_requests_path)
        request_cursor = request_db.cursor()    

        #Check if the user has any metar requests
        sql = "SELECT * FROM Requests WHERE userId = ?"
        request_cursor.execute(sql, (interaction.user.id,))
        result = request_cursor.fetchall()
        if result == []:
            await interaction.response.send_message("You don't have any metar requests", ephemeral=True)
        else:
            embed = discord.Embed(
                title="**Your Requests:**",
                color=discord.Color.blue()
            )
            requests = ""
            for request in result:
                requests += f"Airport: {request[1]}, requests left: {request[2]}\n"
            
            embed.description=requests
            await interaction.response.send_message("Here are your requests: ", embed=embed, ephemeral=True)
        
        request_db.close()
    
    @app_commands.command(name="zulu_time", description="Returns the current zulu time")
    async def zulu_time(self, interaction:discord.Interaction):
        current_time = get_current_zulu()
        current_time = str(current_time) + "Z"
        await interaction.response.send_message(f"The current zulu time is: `{current_time}`")
    
    @app_commands.command(name="baro-converter", description="Converts an altimeter value to it's equivalent in hpa or inhg")
    @app_commands.describe(value="The value we want to convert")
    async def baro_converter(self, interaction:discord.Interaction, value:float):
        if value > 1000: #value is in hpa
            converted = hpa_to_inhg(value)
            await interaction.response.send_message(f"{value:.0f} hpa in inhg would be: {converted} inhg")
        else:
            converted = inhg_to_hpa(value)
            await interaction.response.send_message(f"{value:.2f} in inhg would be: {int(converted)} hpa")


            

    @tasks.loop(minutes=1)
    async def send_metar(self):
        request_db = sqlite3.connect(db_requests_path)
        request_cursor = request_db.cursor()
        sql = "SELECT * FROM Requests"
        request_cursor.execute(sql)
        users = request_cursor.fetchall()

        current_time = self.get_time()

        if users != []:
            for user in users:
                if int(user[3]) < current_time:
                    user_target = await self.bot.fetch_user(user[0])
                    metar_raw = get_metar(user[1], False)

                    if metar_raw == False or metar_raw == None:
                        await user_target.send(f"Hey there was an issue getting the metar for `{user[1]}`, I will try again in 5 minutes. If I can't get it then I'll wait another 5 minutes and reach back to you with the results")
                        tries = 0
                        while tries != 2:
                            await asyncio.sleep(300)
                            metar_raw = get_metar(user[1], False)
                            if metar_raw:
                                break
                            else:
                                tries += 1

                    if metar_raw == False or metar_raw == None:     #If the metar couldn't be grabbed 
                        await user_target.send(f"Hey I've tried getting the metar for `{user[1]}`. But the service doesn't seem to be responding currently, I will try sending you the metar next cycle")
                    else:
                        metar_fancy = self.get_metar_embed(metar_raw)
                        await user_target.send(f"Hey, here's the current metar for `{user[1]}`", embed=metar_fancy)
                    
                    if user[2] == 1:
                        sql = "DELETE FROM Requests WHERE userId = ? AND airportICAO = ?"
                        request_cursor.execute(sql, (user[0], user[1]))
                    else:
                        sql = "UPDATE Requests SET calls = ?, nextCall = ? WHERE userId = ? AND airportICAO = ?"
                        next_call = self.get_time() + 3600
                        request_cursor.execute(sql, ((user[2] - 1), next_call, user[0], user[1]))
                else:
                    continue

        request_db.commit()
        request_db.close()

             
async def setup(bot):
    await bot.add_cog(Metar(bot))