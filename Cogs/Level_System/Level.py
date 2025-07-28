import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="level", description="Shows the current level and xp values for a member")
    @app_commands.describe(member="The member to check")
    async def level(self, interaction:discord.Interaction, member:discord.Member = None):

        if member == None:
            member = interaction.user

        db = await aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()

        guild_id = interaction.guild_id

        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild_id}'" #check if the guild has a table
        await cursor.execute(sql)
        result = await cursor.fetchall()  
        if not result:
            await interaction.response.send_message("I don't have any information about this server in my database.", ephemeral=True)
            await db.close()
            return

        sql = f'SELECT * FROM "{guild_id}" WHERE userId = ?'
        await cursor.execute(sql, (member.id,))
        result = await cursor.fetchall()
        if result == []:
            await interaction.response.send_message("I don't have information about this user.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{member.name} is level {result[0][3]} and needs {abs(result[0][1] - result[0][2])}xp to reach the next level.")

        await db.close()


async def setup(bot):
    await bot.add_cog(Level(bot))