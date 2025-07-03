import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="enable_custom_roles", description="Enables or disables custom roles on this server")
    @commands.has_guild_permissions(manage_messages=True)
    @app_commands.describe(input="True if you want to enable them, False if not")
    async def enable_roles(self, interaction:discord.Interaction, input:bool):
        db = sqlite3.connect("db_exp.db")
        cursor = db.cursor()

        sql = "UPDATE Guilds SET customRoles = ? WHERE id = ?"
        try:
            cursor.execute(sql, (input, interaction.guild.id))
        except Exception:
            await interaction.response.send_message("This server is not in my database. Pleas send a message so I can register it", ephemeral=True)
            db.close()
            return
        db.commit()
        db.close()
        if input == True:
            await interaction.response.send_message("Custom roles have been enabled in this server.")
        else:
            await interaction.response.send_message("Custom roles have been disabled in this server.")

    @app_commands.command(name="custom_role", description="Creates or updates your role")
    @app_commands.describe(name="The name of your role",
        color="Hexadecimal value of the color of the role",
        remove="DELETES your role. If this is True, then it doesn't matter what you put in color"
        )
    async def custom_role(self, interaction:discord.Interaction, name:str, color:str, remove:bool=False):
        await interaction.response.defer()
        guild = interaction.guild

        db = sqlite3.connect("db_exp.db")
        cursor = db.cursor()

        sql = f"SELECT role FROM '{guild.id}' WHERE userId = ?"
        cursor.execute(sql, (interaction.user.id,))
        role_id = cursor.fetchone()[0]

        sql = "SELECT customRoles FROM Guilds WHERE id = ?"
        cursor.execute(sql, (guild.id,))
        allow_roles = cursor.fetchone()[0]

        if allow_roles == False or allow_roles == None:
            await interaction.followup.send("This server does not have custom roles enabled.")
            db.close()
            return

        try:
            if not color.startswith("#"):
                color = "#" + color
            role_color = discord.Color(int(color.strip("#"), 16))
        except ValueError:
            await interaction.followup.send("Invalid hex color format. Use something like `#ff0000`")
            return
        
        sql = f"SELECT role FROM '{guild.id}' WHERE userId = ?"
        cursor.execute(sql, (interaction.user.id,))
        role_id = cursor.fetchone()[0]

        if role_id:
            role = guild.get_role(role_id)
        else:
            role = None
        
        try:
            if role:
                # Remove role
                if remove:
                    await role.delete(reason="Asked by the user")
                    sql = f"UPDATE '{guild.id}' SET role = NULL WHERE userId = ?"
                    cursor.execute(sql, (interaction.user.id,))
                    db.commit()
                    db.close()
                    await interaction.followup.send("I have deleted your role.")
                    return
                # Update role
                await role.edit(color=role_color, name=name)
                await interaction.followup.send(f"I have updated your role, it's now called {name} with the color {color}")
            else:   # Create role
                role = await guild.create_role(name=name, color=role_color)
                await interaction.user.add_roles(role)
                await interaction.followup.send(f"I have created your role {name}, with the color {color}")
            
            sql = f"UPDATE '{guild.id}' SET role = ? WHERE userId = ?"
            cursor.execute(sql, (role.id, interaction.user.id))
            db.commit()
            db.close()

        except discord.Forbidden:
            await interaction.followup.send("I do not have the permission to modify roles.")
            db.close()
        

async def setup(bot):
    await bot.add_cog(Roles(bot))