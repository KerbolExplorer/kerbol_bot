import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

class Random_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def sincount(self, ctx):
        db = await aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()

        sql = "SELECT sinCount FROM Guilds WHERE id = ?"
        await cursor.execute(sql, (ctx.guild.id,))

        sin_count = await cursor.fetchone()
        await db.close()
        await ctx.send(f"This server has sinned {sin_count[0]} times.")

    @commands.command()
    async def amogus(self, ctx):
        await ctx.send(chr(sum(range(ord(min(str(not())))))))

async def setup(bot):
    await bot.add_cog(Random_commands(bot))