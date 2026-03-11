import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add-reaction-role", description="Add a reaction role to a message")
    @commands.has_guild_permissions(manage_messages=True)
    @app_commands.describe(emoji="Emoji the role will be assigned to",
                           role="Role that will be assigned upon reaction",
                           message_link="Link to the message to add the reaction role to. The message must be sent by Orion.")
    async def set_role_message(self, interaction:discord.Interaction, emoji:str, role:discord.Role, message_link:str):
        try:
            message_data = message_link.split("/")
            message_id = message_data[-1]
            channel_id = message_data[-2]

            channel:discord.TextChannel = await self.bot.fetch_channel(channel_id)

            message:discord.Message = await channel.fetch_message(message_id)
        except Exception as e:
            await interaction.response.send_message("The message link was not valid")
            return

        if message.author.id != self.bot.user.id:
            await interaction.response.send_message("The message must be sent by me, use `/say` to make me send a message.", ephemeral=True)
            return
        
        db = await aiosqlite.connect("roles.db")
        cursor = await db.cursor()

        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{channel.guild.id}'"
        await cursor.execute(sql)
        result = await cursor.fetchall()
        if not result:
            sql = f"CREATE TABLE '{channel.guild.id}' (id INTEGER, level INTEGER, msgId INTEGER, chnlId INTEGER, emoji TEXT, isTopRole INTEGER)"
            await cursor.execute(sql)
        
        
        sql = f"INSERT INTO '{channel.guild.id}' (id, level, msgId, chnlId, emoji, isTopRole) VALUES (?, ?, ?, ?, ?, ?)"    # We add the guild data to the guilds table
        await cursor.execute(sql, (role.id, 0, message_id, channel_id, emoji, 0))
        await db.commit()
        await db.close()
        
        await message.add_reaction(emoji)
        await interaction.response.send_message("Done!", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_author_id != self.bot.user.id:
            return
        elif payload.user_id == self.bot.user.id:
            return
        else:

            db = await aiosqlite.connect("roles.db")
            cursor = await db.cursor()

            # Check if the table exists, if it doesn't we just ignore it.
            sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{payload.guild_id}'"
            await cursor.execute(sql)
            result = await cursor.fetchall()
            if not result:
                await db.close()
                return

            sql = f"SELECT * FROM '{payload.guild_id}' WHERE msgId = ? AND emoji = ?"
            await cursor.execute(sql, (payload.message_id, str(payload.emoji)))
            role_data = await cursor.fetchone()

            member:discord.Member = payload.member

            guild:discord.Guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_data[0])
            
            await member.add_roles(role)
            await db.close()
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        else:

            db = await aiosqlite.connect("roles.db")
            cursor = await db.cursor()

            # Check if the table exists, if it doesn't we just ignore it.
            sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{payload.guild_id}'"
            await cursor.execute(sql)
            result = await cursor.fetchall()
            if not result:
                await db.close()
                return
            
            emoji = str(payload.emoji)

            sql = f"SELECT * FROM '{payload.guild_id}' WHERE msgId = ? AND emoji = ?"
            await cursor.execute(sql, (payload.message_id, emoji))
            role_data = await cursor.fetchone()


            guild:discord.Guild = self.bot.get_guild(payload.guild_id)
            member:discord.Member = await guild.fetch_member(payload.user_id)
            role = guild.get_role(role_data[0])

            #channel:discord.TextChannel = self.bot.get_channel(payload.channel_id)
            #message:discord.Message = await channel.fetch_message(payload.message_id)
            
            await member.remove_roles(role)

            await db.close()
"""
    @app_commands.command(name="enable_custom_roles", description="Enables or disables custom roles on this server")
    @commands.has_guild_permissions(manage_messages=True)
    @app_commands.describe(input="True if you want to enable them, False if not")
    async def enable_roles(self, interaction:discord.Interaction, input:bool):
        db = await aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()

        sql = "UPDATE Guilds SET customRoles = ? WHERE id = ?"
        try:
            await cursor.execute(sql, (input, interaction.guild.id))
        except Exception:
            await interaction.response.send_message("This server is not in my database. Please send a message so I can register it", ephemeral=True)
            await db.close()
            return
        await db.commit()
        await db.close()
        if input == True:
            await interaction.response.send_message("Custom roles have been enabled in this server.")
        else:
            await interaction.response.send_message("Custom roles have been disabled in this server.")

    @app_commands.command(name="custom_role", description="Creates or updates your role")
    @app_commands.describe(name="The name of your role",
        color="Hexadecimal value of the color of the role",
        remove="DELETES your role. If this is True, then it doesn't matter what you put in color"
        )
    async def custom_role(self, interaction:discord.Interaction, name:str=None, color:str=None, remove:bool=False):
        await interaction.response.defer(ephemeral=True)

        if name is None and color is None and remove is False:
            await interaction.followup.send("You need to at least edit something")
            return

        guild = interaction.guild

        db = await aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()

        sql = f"SELECT role FROM '{guild.id}' WHERE userId = ?"
        await cursor.execute(sql, (interaction.user.id,))
        role_id = (await cursor.fetchone())[0]

        sql = "SELECT customRoles FROM Guilds WHERE id = ?"
        await cursor.execute(sql, (guild.id,))
        allow_roles = (await cursor.fetchone())[0]

        if allow_roles == False or allow_roles == None:
            await interaction.followup.send("This server does not have custom roles enabled.")
            await db.close()
            return
        
        sql = f"SELECT role FROM '{guild.id}' WHERE userId = ?"
        await cursor.execute(sql, (interaction.user.id,))
        role_id = (await cursor.fetchone())[0]

        if role_id:
            role = guild.get_role(role_id)
        else:
            role = None
        
        if name == None:
            name = role.name
        
        if color == None:
            color = str(hex(role.color.value))

        try:
            if not color.startswith("#"):
                color = "#" + color
            role_color = discord.Color(int(color.strip("#"), 16))
        except ValueError:
            await interaction.followup.send("Invalid hex color format. Use something like `#ff0000`")
            return
        
        try:
            if role:
                # Remove role
                if remove:
                    await role.delete(reason="Asked by the user")
                    sql = f"UPDATE '{guild.id}' SET role = NULL WHERE userId = ?"
                    await cursor.execute(sql, (interaction.user.id,))
                    await db.commit()
                    await db.close()
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
            await cursor.execute(sql, (role.id, interaction.user.id))
            await db.commit()
            await db.close()

        except discord.Forbidden:
            await interaction.followup.send("I do not have the permission to modify roles.")
            await db.close()
    
    # Links roles with the users
    @commands.command()
    async def sync(self, ctx : commands.Context):
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You need to have the manage roles permission to use this command")
            return
        substring = "unlinked"
        guild = ctx.guild

        matching_roles = []

        db = await aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()

        for role in guild.roles:
            if substring in role.name:
                matching_roles.append(role)

        if len(matching_roles) == 0:
            await ctx.send("No unlinked roles found")
            return

        for role in matching_roles:
            if len(role.members) > 1:
                await ctx.send(f"Did not link role {role} because more than 1 member has it")
                continue
            for member in role.members:
                sql = f"UPDATE '{guild.id}' SET role = ? WHERE userId = ?"
                await cursor.execute(sql, (role.id, member.id))
                clean_name = role.name.replace(substring, "")
                await role.edit(name=clean_name)
        await db.commit()
        await db.close()
        await ctx.send("Valid roles have been linked.")"""

async def setup(bot):
    await bot.add_cog(Roles(bot))