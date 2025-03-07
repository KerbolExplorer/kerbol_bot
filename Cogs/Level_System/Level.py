import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="level", description="Shows the current level and xp values for a member")
    async def level(self, interaction:discord.Interaction, member:discord.Member = None):

        if member == None:
            member = interaction.user

        db = sqlite3.connect("db_exp.db")
        cursor = db.cursor()

        guild_id = interaction.guild_id

        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild_id}'" #check if the guild has a table
        cursor.execute(sql)
        result = cursor.fetchall()  
        if not result:
            await interaction.response.send_message("I don't have any information about this server in my database.", ephemeral=True)
            db.close()
            return

        sql = f'SELECT * FROM "{guild_id}" WHERE id = ?'
        cursor.execute(sql, (member.id,))
        result = cursor.fetchall()
        if result == []:
            await interaction.response.send_message("I don't have information about this user.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{member.name} is level {result[0][2]} and needs {abs(result[0][1] - result[0][3])}xp to reach the next level.")

        db.close()


async def setup(bot):
    await bot.add_cog(Level(bot))