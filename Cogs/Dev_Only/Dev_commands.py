import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

admin = os.getenv("ADMIN")

class Dev_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def verify_messenger(self, id):
        if int(id) != int(admin):
            return False
        else:
            return True

    @commands.command()
    async def test(self, ctx):
        user_id = ctx.author.id
        if self.verify_messenger(user_id) == True:
            await ctx.send("This works")
        else:
            return


async def setup(bot):
    await bot.add_cog(Dev_commands(bot))