import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

class Server(commands.Cog):
    def __init__(self, bot, db, cursor):
        self.bot = bot
        self.db = db
        self.cursor = cursor

    @app_commands.command(name="server", description="Gets information about the server")
    async def server(self, interaction:discord.Interaction):
        embed = discord.Embed(
            color = interaction.user.color,
            title=interaction.guild.name
        )
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.add_field(name="Total members:", value=interaction.guild.member_count, inline=False)
        embed.add_field(name="Created on: ", value=interaction.guild.created_at.strftime("%d-%m-%Y"), inline=False)

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="welcome_message", description="Assigns an entry message for the server")
    @app_commands.describe(message="The message that will be said when someone enters the server. If it's left blank, the welcome message will be disables")
    async def welcome_message(self, interaction:discord.Interaction, message:str=None):
        await interaction.response.defer()

        if message == "NULL":
            await interaction.followup.send("The welcome message cannot be 'NULL'")
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("You do not have permissions to execute this command")
            return


        if message:
            sql = "UPDATE 'Guilds' SET welcomeMessage = ? WHERE id = ?"
            await self.cursor.execute(sql, (message, interaction.guild_id))
            await interaction.followup.send("Correctly set the welcome message!")
        else:
            sql = "UPDATE 'Guilds' SET welcomeMessage = ? WHERE id = ?"
            await self.cursor.execute(sql, ("NULL", interaction.guild_id))
            await interaction.followup.send("The welcome message has been removed")
        
        await self.db.commit()
    
    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        channel = member.guild.system_channel
        if channel:
            sql = "SELECT welcomeMessage FROM 'Guilds' WHERE id = ?"
            await self.cursor.execute(sql, (member.guild.id,))
            message = await self.cursor.fetchone()

            if message == None or message == "NULL":
                return
            await channel.send(f"{member.mention}\n{message[0]}")


async def setup(bot):
    db = await aiosqlite.connect("db_exp.db")
    cursor = await db.cursor()
    await bot.add_cog(Server(bot, db, cursor))
