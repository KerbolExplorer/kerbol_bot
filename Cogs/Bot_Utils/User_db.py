import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

class User_db(commands.Cog):
    def __init__(self, bot, db, cursor):
        self.bot = bot
        self.db = db
        self.cursor = cursor
        self.bot.loop.create_task(self.create_table())

    async def create_table(self):
        sql = "CREATE TABLE IF NOT EXISTS 'Users' (userId INTEGER, simbrief TEXT)"
        await self.cursor.execute(sql)
    
    

async def setup(bot):
    db = await aiosqlite.connect("db_exp.db")
    cursor = await db.cursor()
    await bot.add_cog(User_db(bot, db, cursor))