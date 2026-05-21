import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import random

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

    @commands.command()
    async def ralsei(self, ctx:commands.Context):
        await ctx.send("<:ralseiluv:1481270587266564147>")
    
    @commands.command()
    async def kerbol(self, ctx):
        await ctx.send("<:kerbol:1312437693979955230>")
    
    @commands.command()
    async def alusin(self, ctx):
        responses = ("Ella quiere conmigo pero nah", "Se lo tienen muy creido, no tienen ni idea",
                     "Le ganaria a campeones de tekken masheando botones",
                     "He llegado al punto de no retorno", "Rocket League es el juego mas mecanicamente complejo de la historia",
                     "No hay fisicamente tiempo para estudiar", "9 meses ya", "Ya está, ya toqué fondo, que mas quiere la vida de mi?",
                     "Pues nada, ya me jodieron el inicio de la vida adulta")
        
        await ctx.send(f'"*{random.choice(responses)}"*')


async def setup(bot):
    await bot.add_cog(Random_commands(bot))