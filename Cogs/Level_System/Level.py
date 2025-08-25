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
        result = await cursor.fetchone()

        if result == None:
            await interaction.response.send_message("I don't have information about this user.", ephemeral=True)
            await db.close()
            return

        bar_length = 20
        filled_length = int(round(bar_length * result[1]/result[2]))
        percentage = int(round((result[1]*100)/result[2]))

        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        string = f"[{bar}] {percentage}%"

        embed = discord.Embed(
            title=f"Level {result[3]}",
            color=member.color,
            description=f"You need {abs(result[1] - result[2])}xp to reach the next level."
        )
        embed.add_field(name="\u200b", value=string, inline=False)
        embed.set_thumbnail(url=member.display_avatar)

        await interaction.response.send_message(embed=embed)

        await db.close()


async def setup(bot):
    await bot.add_cog(Level(bot))