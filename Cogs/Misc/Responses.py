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
            response = ("Hmm?", "Huh?", "What?", "Need anything?", "Make it quick")
            await message.channel.send(response[random.randint(0, len(response) -1)])

async def setup(bot):
    await bot.add_cog(Responses(bot))