import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timezone
import asyncio
import sqlite3
import os
from .Aviation_Utils.Aviation_Utils import get_metar
from .Aviation_Utils.Aviation_Math import hpa_to_inhg

db_requests_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "requests.db")

class Metar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not self.send_metar.is_running():
            self.send_metar.start()

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
                    'TCU' : 'Towering cumulus clouds'
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

    @app_commands.command(name="metar", description="Gets the metar for an airport")
    @app_commands.describe(airport="Icao code of the airport")
    async def metar(self, interaction:discord.Interaction, airport:str):
        metar = get_metar(airport, False)

        if metar == False:
            await interaction.response.send_message("There was an issue getting this metar.", ephemeral=True)
        elif metar == None:
            await interaction.response.send_message("This metar is not available.", ephemeral=True)
        else:
            embed = self.get_metar_embed(metar)
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="metar_request", description="Have Solgaleo periodically send you the metar for an airport")
    @app_commands.describe(
        airport="Icao code of the airport",
        hours="How many hours you want to be reminded for"
    )
    async def metar_request(self, interaction:discord.Interaction, airport:str, hours:int):
        metar = get_metar(airport, False)

        if metar == False:
            await interaction.response.send_message("There was an issue getting this metar.", ephemeral=True)
        elif metar == None:
            await interaction.response.send_message("This metar is not available.", ephemeral=True)
        else:
            request_db = sqlite3.connect(db_requests_path)
            request_cursor = request_db.cursor()
            sql = "SELECT * FROM Requests"
            request_cursor.execute(sql)
            result = request_cursor.fetchall()
            if result == []:
                sql = "INSERT INTO Requests (userId, airportICAO, calls, firstLoop) VALUES (?, ?, ?, ?)"
                request_cursor.execute(sql, (interaction.user.id, airport.upper(), hours, True))
            else:
                sql = "INSERT INTO Requests (userId, airportICAO, calls, firstLoop) VALUES (?, ?, ?, ?)"
                request_cursor.execute(sql, (interaction.user.id, airport.upper(), hours, False))
            request_db.commit()
            request_db.close()

            await interaction.response.send_message(f"Roger that, I'll DM you the metar of `{airport}` during {hours} hours. If you wish to cancel, do `/metar_cancel`")
        if not self.send_metar.is_running():
            self.send_metar.start()

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
            await interaction.response.send_message("You don't have any metar requests")
        else:
            if airport == None:
                sql = "DELETE FROM Requests WHERE userId = ?"
                request_cursor.execute(sql, (interaction.user.id,))
                await interaction.response.send_message("All of your metar requests have been cancelled")
            else:
                sql = "SELECT * FROM Requests WHERE userId = ? AND airportICAO = ?"
                request_cursor.execute(sql, (interaction.user.id, airport.upper()))

                if result == []:
                    await interaction.response.send_message(f"Couldn't find any requests for `{airport.upper()}`")
                else:
                    sql= "DELETE FROM Requests WHERE userId = ? AND airportICAO = ?"
                    request_cursor.execute(sql, (interaction.user.id, airport.upper()))
                    await interaction.response.send_message(f"Alright, I've cancelled the metar requests for `{airport.upper()}`")

        request_db.commit()
        request_db.close()        

    @tasks.loop(minutes=1)
    async def send_metar(self):
        request_db = sqlite3.connect(db_requests_path)
        request_cursor = request_db.cursor()
        sql = "SELECT * FROM Requests"
        request_cursor.execute(sql)
        users = request_cursor.fetchall()

        if users != []:
            for user in users:
                if user[3] == True:     #This is so the dm isn't send the second the command is executed
                    sql = "UPDATE Requests SET firstLoop = ? WHERE userId = ? AND airportICAO = ?"
                    request_cursor.execute(sql, (False, user[0], user[1]))
                    continue
                user_target = await self.bot.fetch_user(user[0])
                metar_raw = get_metar(user[1], False)

                if metar_raw == False or metar_raw == None:  #If there was an error grabing the metar, we'll give it 5 minutes before trying again, we do this twice and send an error if it doesn't work
                    await user_target.send(f"Hey there was an issue getting the metar for `{user[1]}`, I will try again in 5 minutes. If I can't get it then I'll wait another 5 minutes and reach back to you with the results")
                    tries = 0
                    while tries != 2:
                        await asyncio.sleep(300)
                        metar_raw = get_metar(user[1], False)
                        if metar_raw != False or metar_raw != None:
                            break
                        else:
                            tries += 1
                
                if metar_raw == False or metar_raw == None:     #If the metar couldn't be grabbed 
                    await user_target.send(f"Hey I tried getting the metar for `{user[1]}`. But the service doesn't seem to be responding currently, I will try sending you the metar next cycle")
                else:
                    metar_fancy = self.get_metar_embed(metar_raw)
                    await user_target.send(f"Hey, here's the current metar for `{user[1]}`", embed=metar_fancy)

                if user[2] == 1:
                    sql = "DELETE FROM Requests WHERE userId = ? AND airportICAO = ?"
                    request_cursor.execute(sql, (user[0], user[1]))
                else:
                    sql = "UPDATE Requests SET calls = ? WHERE userId = ? AND airportICAO = ?"
                    request_cursor.execute(sql, ((user[2] - 1), user[0], user[1]))
        else:
            self.send_metar.stop()
        request_db.commit()
        request_db.close()

             
async def setup(bot):
    await bot.add_cog(Metar(bot))