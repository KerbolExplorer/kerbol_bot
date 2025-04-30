import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

admin = os.getenv("ADMIN")

class Dev_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def verify_messenger(self, id):
        if int(id) != int(admin):
            return False
        else:
            return True

    # Like the ping command but even more barebones
    @commands.command()
    async def test(self, ctx):
        user_id = ctx.author.id
        if self.verify_messenger(user_id) == True:
            await ctx.send("This works")
        else:
            return
    
    # Unloads the responses cog to make the bot shut up when responded.
    @commands.command()
    async def shutup(self, ctx, time: int = 60):
        user_id = ctx.author.id
        if self.verify_messenger(user_id) == True:
            await self.bot.unload_extension("Cogs.Misc.Responses")
            await ctx.message.add_reaction("✅")
            await asyncio.sleep(time)
            await self.bot.load_extension("Cogs.Misc.Responses")
        else:
            await ctx.send("And who do you think you are to tell me that?!")

    # Unloads the cog with the specified path. 
    @commands.command()
    async def unload(self, ctx, cog: str, time: int = 60):
        user_id = ctx.author.id
        if self.verify_messenger(user_id) == True:
            if cog is None:
                await ctx.send("Please send the path of the cog you want to unload")
                await ctx.message.add_reaction("❌")
                return
            elif cog == "Cogs.Dev_Only.Dev_commands":
                await ctx.send("This cog can not be disabled.")
                await ctx.message.add_reaction("❌")
                return
            else:
                await self.bot.unload_extension(cog)
                await ctx.message.add_reaction("✅")
                await asyncio.sleep(time)
                await self.bot.load_extension(cog)
                await ctx.author.send(f"The cog with the path `{cog}` has been re-enabled after a manual shutdown.")
                return
        else:
            return
        

                

async def setup(bot):
    await bot.add_cog(Dev_commands(bot))