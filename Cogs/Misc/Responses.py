import discord
from discord import app_commands
from discord.ext import commands
import random

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

async def setup(bot):
    await bot.add_cog(Responses(bot))