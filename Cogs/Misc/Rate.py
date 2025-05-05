import discord
from discord import app_commands
from discord.ext import commands
import hashlib

class Rate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rate", description="Rates something")
    @app_commands.describe(item="What is going to be rated")
    async def rate(self, interaction:discord.Interaction, item: str):
        if item == "<@631770724649926657>" or item == "<@573578910625955850>" or item.lower() == "solgaleo":
            await interaction.response.send_message("I humbly rate myself a 10/10")
            return
        elif item == "<@442728041115025410>" or item.lower() == "kerbol":
            await interaction.response.send_message("Yeah he is pretty neat, 10/10")
            return

        hash_object = hashlib.sha256(item.lower().encode())
        hash_digest = hash_object.hexdigest()

        value = int(hash_digest, 16)
        rating = (value % 10) + 1

        await interaction.response.send_message(f"I rate {item} a {rating}/10")


async def setup(bot):
    await bot.add_cog(Rate(bot))