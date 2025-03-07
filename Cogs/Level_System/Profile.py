import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="profile",description="Get user's profile")
    async def profile(self, interaction:discord.Interaction,member:discord.Member = None):         #TODO add dropdown menu to change between profiles

        if member == None:
            member = interaction.user

        db = sqlite3.connect("db_exp.db")
        cursor = db.cursor()

        guild_id = interaction.guild_id
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild_id}'" #check if the guild has a table
        cursor.execute(sql)
        result = cursor.fetchall()  
        if not result:
            result = [(None,"0", "1", "100")]
        else:
            sql = f'SELECT * FROM "{guild_id}" WHERE id = ?'
            cursor.execute(sql, (member.id,))
            result = cursor.fetchall()
            if result == []:
                result = [(None,"0", "1", "100")]

        if member.id == 442728041115025410:
            title = f"{member.display_name}'s profile :sparkles:"
        else:
            title = f"{member.display_name}'s profile"

        embed = discord.Embed(
            color=member.color,
            title=title
        )
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name="Name", value=member.display_name)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Level", value=f"{result[0][2]}")
        embed.add_field(name="XP", value=f"XP: {result[0][1]}/{result[0][3]}")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        db.close() 


async def setup(bot):
    await bot.add_cog(Profile(bot))