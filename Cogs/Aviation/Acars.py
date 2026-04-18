import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from hoppie_connector import *


class Acars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logon = load_dotenv("HOPPIE")
        self.connection:HoppieConnector = HoppieConnector(station_name="ORI", logon=self.logon)

        # Begin polling task
        if not self.hoppie_polling.is_running():
            self.hoppie_polling.start()
    

    @tasks.loop(seconds=67)
    async def hoppie_polling(self):
        print(self.connection.poll())
    


async def setup(bot):
    await bot.add_cog(Acars(bot))