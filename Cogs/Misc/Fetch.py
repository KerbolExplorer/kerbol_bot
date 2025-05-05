import discord
from discord import app_commands
from discord.ext import commands
import random

class Fetch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="fetch", description="Throw a stick at Solgaleo and he *should* return it")
    async def fetch(self, interaction:discord.Interaction):
        responses = (
            "Heres the stick back!", "Heres the stick back, careful with the fire on the tip!", "Uh...where did you launch it?"
            "I think we lost the stick", "Why don't YOU go fetch it for a change?", "I don't feel like it", "Nuh uh",
            "You are better at throwing exams than sticks", "I've found some weird card in japanese with your name on it, here you go!"
            "...You threw it into the river", "Have this suspicious looking eye I found!", "I've found a golden scar! **HOLY SHIT**", 
            "I've found a blue ocarina", "Do you know who else fetched sticks?", "I've found an onion!", "Have a green emerald I found!", 
            "Here's a gun I found on the floor, it seems to speak!", "Here's the golden arrow you threw!", "Found a green leak!, Popipo!",
            "I've found the One piece!, no you can't see what it is", "I've found a happy meal with one piece characters on it",
            "I've found you a girlfriend XDXDXDXDXDXDXDXDXDXDXDXDXDXDXDXDXDXDXD", "I've found a bad Persona song!", "Found a couple of Tarot cards", 
            "I've found your Tweets from 7 years ago...", "I've found something that doesn't exist!"
        )

        await interaction.response.send_message(random.choice(responses))

async def setup(bot):
    await bot.add_cog(Fetch(bot))