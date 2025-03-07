import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="leaderboard", description="Displays the leaderboard for the server")
    async def leaderboard(self, interaction:discord.Interaction):
        guild_id = interaction.guild_id
        cap = 0
        db = sqlite3.connect("db_exp.db")
        cursor = db.cursor()

        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild_id}'" #check if the guild has a table
        cursor.execute(sql)
        result = cursor.fetchall()  
        if not result:
            await interaction.response.send_message("I don't have any information about this server in my database.", ephemeral=True)
            db.close()
            return

        sql = f'SELECT * FROM "{guild_id}"'

        cursor.execute(sql)
        result = cursor.fetchall()
        db.close()
        result.sort(key=lambda x: x[1], reverse=True)
        member_list = []

        for member in result:
            cap += 1
            if cap >= 10:
                break
            user = await self.bot.fetch_user(member[0])
            member_data = f"{user}, level: {member[2]}"
            member_list.append(member_data)

        returned_data = '\n'.join(member_list)

        embed = discord.Embed(
            color=interaction.user.color,
            title=f"{interaction.guild.name} leaderboard"
        )
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.add_field(name="Member list:", value= returned_data)
        embed.set_footer(text="Showing the top 10 members of the server")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))