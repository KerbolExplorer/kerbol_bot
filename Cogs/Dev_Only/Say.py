import discord
from discord import app_commands
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="say", description="Have Solgaleo say something for you")
    @app_commands.describe(
        message="The message Solgaleo will say",
        message_id="The id of the message to reply to"
    )
    async def say(self, interaction:discord.Interaction, message: str, message_id: str = None):
        if message_id != None:
            reply_message = await interaction.channel.fetch_message(int(message_id))
            await interaction.channel.send(content=message, reference=reply_message)
        else:
            await interaction.channel.send(message)

async def setup(bot):
    await bot.add_cog(Say(bot))