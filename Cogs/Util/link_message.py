import discord
from discord import app_commands
from discord.ext import commands
import re


class LinkMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_regex = re.compile(
            r"https:\/\/(?:canary\.|ptb\.)?discord(?:app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)"
                                        )
        self.enabled = False
    
    @commands.Cog.listener('on_message')
    async def link_message(self, message):
        if self.enabled == False:
            return
        
        match = self.message_regex.search(message.content)

        if match:
            guild_id, channel_id, message_id = map(int, match.groups())

            channel:discord.TextChannel = self.bot.get_channel(channel_id)

            linked_message:discord.Message = await channel.fetch_message(message_id)

            await channel.send(linked_message.content)


async def setup(bot):
    await bot.add_cog(LinkMessage(bot))