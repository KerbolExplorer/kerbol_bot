import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
from .Aviation_Utils.Aviation_Utils import send_hoppie_telex
from hoppie_connector import *
import os


class Acars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logon = os.getenv("HOPPIE")
        self.connection:HoppieConnector = HoppieConnector(station_name="ORI", logon=self.logon)

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
        print("Response:", response)
        if type(response) == str or response == False:
            await ctx.send(f"Error: {response}")
        else:
            await ctx.send("Message sent!")
    

    @tasks.loop(seconds=67)
    async def hoppie_polling(self):
        print(self.connection.poll())
    


async def setup(bot):
    await bot.add_cog(Acars(bot))