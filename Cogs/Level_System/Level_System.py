import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import sqlite3

class Level_System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    cooldown_members = set()

    @commands.Cog.listener('on_message')
    async def xp_give(self, message):
        if message.author.bot == False and message.author.id not in Level_System.cooldown_members and message.guild:
            Level_System.cooldown_members.add(message.author.id)

            db = sqlite3.connect("db_exp.db")
            cursor = db.cursor()
            user = message.author.id
            guild_id = message.guild.id

            sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild_id}'" #check if the guild has a table
            cursor.execute(sql)
            result = cursor.fetchall()  
            if not result:
                sql = f'CREATE TABLE "{guild_id}" (id INTEGER, xp INTEGER, level INTEGER, xp_next INTEGER)' #if the guild doesn't have any table we create it
                cursor.execute(sql)
            
            sql = f'SELECT * FROM "{guild_id}" WHERE id = ?'  #Now that we are sure that it exists we check if the user has a row in it
            cursor.execute(sql, (user,))
            result = cursor.fetchall()

            if result != []:
                experience = random.randint(15, 25)
                if result[0][1] + experience >= result[0][3]:
                    #update xp 
                    sql = f'UPDATE "{guild_id}" SET xp = ? WHERE id = ?'
                    new_experience = abs(experience + result[0][1])
                    cursor.execute(sql, (new_experience, user,))

                    #update level
                    sql = f'UPDATE "{guild_id}" SET level = ? WHERE id = ?'
                    new_level = result[0][2] + 1
                    cursor.execute(sql, (new_level, user,))

                    #update new required xp
                    sql = f'UPDATE "{guild_id}" SET xp_next = ? WHERE id = ?'
                    xp_next = result[0][3] * 2.5 + 25
                    cursor.execute(sql, (xp_next, user,))
                    db.commit()
                    db.close()
                else:
                    sql = f'UPDATE "{guild_id}" SET xp = ? WHERE id = ?'
                    new_experience = abs(experience + result[0][1])
                    cursor.execute(sql, (new_experience, user,))
                    db.commit()
                    db.close()
            else:
                sql = f'INSERT INTO "{guild_id}" (id, xp, level, xp_next) VALUES (?, ?, ?, ?)'
                cursor.execute(sql, (user, 25, 1, 100))

                db.commit()
                db.close()
            await asyncio.sleep(60)
            Level_System.cooldown_members.remove(message.author.id)  

async def setup(bot):
    await bot.add_cog(Level_System(bot))