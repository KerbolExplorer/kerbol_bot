import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

async def setup(bot):
    await bot.add_cog(Server(bot))