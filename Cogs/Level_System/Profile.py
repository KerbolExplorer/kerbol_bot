import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="profile",description="Get user's profile")
    @app_commands.describe(member="The member we want to check")
    async def profile(self, interaction:discord.Interaction,member:discord.Member = None):         #TODO add dropdown menu to change between profiles

        if member == None:
            member = interaction.user

        db = await aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()

        guild_id = interaction.guild_id
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild_id}'" #check if the guild has a table
        await cursor.execute(sql)
        result = await cursor.fetchall()  
        if not result:
            result = [(None,"0", "100", "1")]
        else:
            sql = f'SELECT * FROM "{guild_id}" WHERE userId = ?'
            await cursor.execute(sql, (member.id,))
            result = await cursor.fetchall()
            if result == []:
                result = [(None,"0", "100", "1")]

        if member.id == 442728041115025410:
            title = f"{member.display_name}'s profile :sparkles:"
        else:
            title = f"{member.display_name}'s profile"

        embed = discord.Embed(
            color=member.color,
            title=title
        )
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Name", value=member.display_name)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Level", value=f"{result[0][3]}")
        embed.add_field(name="XP", value=f"XP: {result[0][1]}/{result[0][2]}")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        await db.close() 

    @app_commands.command(name="banner", description="Shows the banner of a user")
    @app_commands.describe(member="The member we want to check")
    async def banner(self, interaction:discord.Interaction, member:discord.Member = None):
        await interaction.response.defer()
        if member == None:
            member = interaction.user
        

        embed = discord.Embed(
            title=f"{member.display_name}'s banner", 
            color=member.color
        )
        
        user = await self.bot.fetch_user(member.id)

        banner = user.banner
        
        if banner == None:
            await interaction.followup.send("This user doesn't have a banner", ephemeral=True)
        else:
            embed.set_image(url=banner.url)
            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))