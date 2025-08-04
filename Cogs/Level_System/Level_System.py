import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
import random
import aiosqlite

class Level_System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup_database())

    async def setup_database(self):
        db = await aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='Guilds'"
        await cursor.execute(sql)
        result = await cursor.fetchall()
        if not result:
            sql = "CREATE TABLE 'Guilds' (id INTEGER, cooldown INTEGER, minGain INTEGER, maxGain INTEGER, customRoles BOOLEAN, sinCount INTEGER)"
            await cursor.execute(sql)
            await db.commit()
            await db.close()
    
    async def add_exp(self, user_data, guild_data, xp_gain):
        db = await aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()
        
        user_id = user_data[0]
        current_xp = user_data[1]
        xp_next = user_data[2]
        level = user_data[3]
        guild_id = guild_data[0]

        total_xp = current_xp + xp_gain

        while total_xp >= xp_next:
            total_xp -= xp_next
            level += 1
            xp_next = int(100 * level ** 1.5)

        current_time = int(datetime.now(timezone.utc).timestamp())
        cooldown_end = current_time + guild_data[1]

        sql = f"UPDATE '{guild_id}' SET xp = ?, xpNext = ?, level = ?, cooldownEnd = ? WHERE userId = ?"

        await cursor.execute(sql, (total_xp, xp_next, level, cooldown_end, user_id))
        await db.commit()
        await db.close()

    @commands.Cog.listener('on_message')
    async def on_message(self, message):
        if message.author.bot == False and message.guild:
            db = await aiosqlite.connect("db_exp.db")
            cursor = await db.cursor()
            user = message.author.id
            guild_id = message.guild.id

            sql = "SELECT * FROM Guilds WHERE id = ?"
            await cursor.execute(sql, (guild_id,))
            result = await cursor.fetchall()
            
            if result == []:    # If the guild is not on the database, create it
                sql = "INSERT INTO Guilds (id, cooldown, minGain, maxGain, customRoles) VALUES (?, ?, ?, ?, ?)"    # We add the guild data to the guilds table
                await cursor.execute(sql, (guild_id, 60, 15, 25, False))
                
                # We then create the guilds own table to store it's users
                sql = f"CREATE TABLE '{guild_id}' (userId INTEGER, xp INTEGER, xpNext INTEGER, level INTEGER, cooldownEnd INTEGER, role INTEGER)" 
                await cursor.execute(sql)

            sql = f"SELECT * FROM '{guild_id}' WHERE userId = ?"
            await cursor.execute(sql, (user,))
            result = await cursor.fetchall()

            sql = "SELECT * FROM Guilds Where id = ?"
            await cursor.execute(sql, (guild_id,))
            guild_result = await cursor.fetchall()
            current_time = int(datetime.now(timezone.utc).timestamp())
            cooldown_end = guild_result[0][1] + current_time

            xp_gain = random.randint(guild_result[0][2], guild_result[0][3])

            if result != []:
                if result[0][4] <= current_time:
                    await self.add_exp(result[0], guild_result[0], xp_gain)
            else:
                sql = f"INSERT INTO '{guild_id}' (userId, xp, xpNext, level, cooldownEnd) VALUES (?, ?, ?, ?, ?)"
                await cursor.execute(sql, (user, xp_gain, 100, 1, cooldown_end))
            await db.commit()
            await db.close()
    
    # Server admin commands
    @app_commands.command(name="xp_cooldown", description="Changes the xp gain cooldown for a server")
    @commands.has_guild_permissions(manage_messages=True)
    async def xp_cooldown(self, interaction:discord.Interaction, cooldown:int):
        db = aiosqlite.connect("db_exp.db")
        cursor = await db.cursor()
        
        sql = "UPDATE Guilds SET cooldown = ? WHERE id = ?"
        try:
            await cursor.execute(sql, (cooldown, interaction.guild.id))
            sql = f"UPDATE '{interaction.guild.id}' SET cooldownEnd = 0"
            await cursor.execute(sql)
        except Exception:
            await interaction.response.send_message("This server is not in my database. Please send a message so I can register it", ephemeral=True)
            await db.close()
            return
        await db.commit()
        await db.close()
        await interaction.response.send_message(f"Updated the cooldown correctly. It is now set to {cooldown} seconds")
            


async def setup(bot):
    await bot.add_cog(Level_System(bot))