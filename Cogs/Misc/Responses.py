import discord
from discord import app_commands
from discord.ext import commands
import random
import aiosqlite

class Responses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener('on_message')
    async def responses(self, message):
        if message.author.bot == False and self.bot.user.mentioned_in(message):
            content = message.clean_content.replace(f"@{self.bot.user.name}", "").strip().lower()

            if content == "am i cute?":
                await message.channel.send("Yes you are :3")
                return
            elif content == ":3":
                await message.channel.send(":3")
                return
            elif content == "you are cute" or content == "cutie":
                await message.channel.send("No u")
                return
            elif content == "you are the best":
                await message.channel.send("ik")
                return
            
            response = ("Hmm?", "Huh?", "What?", "Need anything?", "Make it quick")
            await message.channel.send(random.choice(response))
        elif message.author.bot == False and message.guild:
            content = message.content.lower()
            if "vore" in content:
                await message.reply("https://tenor.com/view/warning-gif-15403397949888856290")
                server_id = message.guild.id

                db = await aiosqlite.connect("db_exp.db")
                cursor = await db.cursor()
                sql = "UPDATE Guilds SET sinCount = COALESCE(sinCount, 0) + 1 WHERE id = ?"
                await cursor.execute(sql, (server_id,))
                await db.commit()
                await db.close()
                return

async def setup(bot):
    await bot.add_cog(Responses(bot))