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
        self.enabled = True
    
    @commands.Cog.listener('on_message')
    async def link_message(self, message):
        if self.enabled == False:
            return
        
        match = self.message_regex.search(message.content)

        if match:
            guild_id, channel_id, message_id = map(int, match.groups())

            channel:discord.TextChannel = self.bot.get_channel(channel_id)

            try:
                linked_message:discord.Message = await channel.fetch_message(message_id)
            except Exception:
                return
            
            if linked_message.embeds != [] and linked_message.content == "":
                return

            quoted_content = "\n".join(
                f"> {line}" for line in linked_message.content.splitlines()
            )

            embed = discord.Embed(
                description=(
                    f"**Originally posted in** {linked_message.channel.mention} "
                    f"**on** <t:{int(linked_message.created_at.timestamp())}:F>\n\n"
                    f"{quoted_content}"
                ),
                timestamp=discord.utils.utcnow(),
                color=discord.Colour.gold()
            )

            embed.set_author(
                name=str(linked_message.author),
                icon_url=linked_message.author.display_avatar.url
            )

            embed.set_footer(
                text=f"Linked by {message.author}"
            )

            await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LinkMessage(bot))