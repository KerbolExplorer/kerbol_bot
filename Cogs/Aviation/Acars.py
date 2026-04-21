import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
from .Aviation_Utils.Aviation_Utils import send_hoppie_telex, get_metar
from hoppie_connector import *
import os
import re
import asyncio
import aiosqlite
from datetime import datetime, timezone

# TODO:
# Implementation with metar command
# Allow for receiving messages
# Execute commands with receiving messages
# Implementation with flightplan command
# 
class Acars(commands.Cog):
    def __init__(self, bot, request_db, request_cursor):
        self.bot = bot
        self.logon = os.getenv("HOPPIE")
        self.connection:HoppieConnector = HoppieConnector(station_name="ORI", logon=self.logon)
        self.request_db:aiosqlite.Connection = request_db
        self.request_cursor:aiosqlite.Cursor = request_cursor

        self.telex_msgs = []

        # Begin polling task
        if not self.hoppie_polling.is_running():
            self.hoppie_polling.start()

    def get_time(self):
        return int(datetime.now(timezone.utc).timestamp())

        # Test command for sending messages
    @commands.command()
    async def send_telex(self, ctx:commands.Context, station, *, message):
        if ctx.author.id != 442728041115025410:
            await ctx.send("Command not available")
            return
        
        response = send_hoppie_telex(station, message)
        if response == True:
            await ctx.send("Message sent!")
        else:
            await ctx.send(f"Error: {response}")
    
    @app_commands.command(name="telex_metar", description="Sends the metar for the requested airport via telex")
    async def telex_metar(self, interaction:discord.Interaction, callsign:str, airport:str):
        callsign = callsign.upper()
        airport = airport.upper()

        metar = get_metar(airport, True)

        message = f"METAR FOR {airport}:\n{metar}"

        response = send_hoppie_telex(callsign, message)
        if response == True:
            await interaction.response.send_message("Message sent!")
        else:
            await interaction.response.send_message(f"Error: {response}")
    

    @tasks.loop(seconds=67)
    async def hoppie_polling(self):
        messages, delay = self.connection.poll()

        for msg in messages:
            print(f"FROM: {msg.get_from_name()}")
            print(f"TO: {msg.get_to_name()}")
            print(f"MSG: {msg.get_message()}")
            print("------")
            # Check if the message corresponds to any command
            # All commands must have 5 characters for the name. Worst case scenario a "." can be used to fill up space.
            pattern = "^([A-Z]{5})(.*)$"

            result = re.split(pattern, msg.get_message())

            if result != None:
                if len(result[1]) != 5:
                    print("failed check 2")
                    continue
                else:
                    result.pop(0)
            else:
                print("failed check 1")
                continue
            
            # Format was at least valid, now we check 
            # TODO: If ICAO = S, stop sending metars.
            # METAR: "METAR {ICAO} {hours}*     *optional"
            if result[0] == "METAR":
                arguments = result[1].split() # [0] icao, [1] hours, optional
                
                if len(arguments) == 2:
                    hours = arguments.pop()
                    sql = "INSERT INTO Requests (userId, airportICAO, calls, nextCall, type, callsign) VALUES (?, ?, ?, ?, ?, ?)"
                    await self.request_cursor.execute(sql, (None, arguments[0], hours, 0, "telex", msg.get_from_name()))
                    await self.request_db.commit()
                
                metar = get_metar(arguments[0])
                await asyncio.sleep(15) # sleep 15 seconds, lowers load on hoppie
                send_hoppie_telex(msg.get_from_name(), metar)

            else:
                # Invalid command, do nothing
                print(f"failed check 3")
                continue



            """
            if type(msg) == TelexMessage:
                if msg in self.telex_msgs:
                    continue
                else:
                    self.telex_msgs.append(msg)
                    print(self.telex_msgs)"""   
    


async def setup(bot):
    db_requests_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "requests.db")
    db = await aiosqlite.connect(db_requests_path)
    cursor = await db.cursor()
    await bot.add_cog(Acars(bot, db, cursor))