import discord
from discord import app_commands
from discord.ext import commands
import random

class Bite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bite", description="Solgaleo bites the selected user")
    async def bite(self, interaction:discord.Interaction, target:discord.Member):
        if (interaction.user.id is target.id):
            self_bite_responses = (
                "Why do you wish for me to bite you?", "If you ask so", "I'll bite you. But I will judge you", "*Solgaleo frowns* Oh you are one of those..."
                )
            await interaction.response.send_message(self_bite_responses[random.randint(0, len(self_bite_responses) -1)])
        elif (target.id is self.bot.user.id):
            await interaction.response.send_message("I'm not biting myself")
        else:
            await interaction.response.send_message(f"*Solgaleo bites hard on {target.display_name}!*")

async def setup(bot):
    await bot.add_cog(Bite(bot))