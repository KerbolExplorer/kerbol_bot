import discord
from discord import app_commands
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="say", description="Have Orion say something for you")
    @app_commands.describe(
        message="The message Orion will say",
        message_id="The id of the message to reply to"
    )
    async def say(self, interaction:discord.Interaction, message: str, message_id: str = None):
        message = message.replace("\\n", "\n")
        if message_id != None:
            reply_message = await interaction.channel.fetch_message(int(message_id))
            await interaction.channel.send(content=message, reference=reply_message)
        else:
            await interaction.channel.send(message)
    
    @commands.command()
    async def edit(self, ctx:commands.Context, message_id:int, new_message:str):  
        new_message = new_message.replace("\\n", "\n")  
        message = await ctx.channel.fetch_message(int(message_id))
        await message.edit(content=str(new_message))

async def setup(bot):
    await bot.add_cog(Say(bot))