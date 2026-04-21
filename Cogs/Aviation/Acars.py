import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
from .Aviation_Utils.Aviation_Utils import send_hoppie_telex, get_metar
from hoppie_connector import *
import os

# TODO:
# Implementation with metar command
# Allow for receiving messages
# Implementation with flightplan command
# 
class Acars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logon = os.getenv("HOPPIE")
        self.connection:HoppieConnector = HoppieConnector(station_name="ORI", logon=self.logon)

        self.telex_msgs = []

        # Begin polling task
        if not self.hoppie_polling.is_running():
            self.hoppie_polling.start()

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
            if type(msg) == TelexMessage:
                if msg in self.telex_msgs:
                    continue
                else:
                    self.telex_msgs.append(msg)
                    print(self.telex_msgs)
    


async def setup(bot):
    await bot.add_cog(Acars(bot))