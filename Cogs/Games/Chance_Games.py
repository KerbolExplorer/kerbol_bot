import discord
from discord import app_commands
from discord.ext import commands
import random

class Chance_Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="coinflip", description="Does a coin flip")
    async def coinflip(self, interaction:discord.Interaction):
        result = random.randint(0, 1)
        if result == 1:
            await interaction.response.send_message("Heads!")
        else:
            await interaction.response.send_message("Tails!")

    @app_commands.command(name="diceroll", description="Rolls a 6 side dice by default")
    @app_commands.describe(sides="How many sides the dice has", dices="How many dices you want to throw")
    async def diceroll(self, interaction:discord.Interaction, sides:int = 6, dices:int = 1):
        #Dice number checks
        if dices < 0:
            await interaction.response.send_message(f"{dices}???")
        elif dices == 0:
            await interaction.response.send_message(f"Of course yes let me throw 0 dices for ya")

        #Sides checks
        if sides < 0:
            await interaction.response.send_message(f"A dice with {sides} sides? Really?")
        elif sides == 0:
            await interaction.response.send_message("Preferably, a dice should have more than 1 side")
        elif sides == 1:
            await interaction.response.send_message("The result is 1, who would have thought")
        elif dices == 1:
            result = random.randint(1, sides)
            if sides == 20:
                if result == 1:
                    await interaction.response.send_message("Damn a 1, that's rough")
                elif result == 20:
                    await interaction.response.send_message("NATURAL 20 LETS FUCKING GO")
                else:
                    await interaction.response.send_message(f"And the result is, {result}!")  
            else: 
                await interaction.response.send_message(f"And the result is, {result}!")
        else:
            current_dice = 1
            total_dices = []
            while current_dice <= dices:
                result = random.randint(1, sides)
                total_dices.append(result)
                print(f"Added dice {current_dice}")
                current_dice += 1
            total = 0
            for dice in total_dices:
                total += dice
            await interaction.response.send_message(
                f"The dices roll as follow: {total_dices}\n"
                f"They all add up to **{total}**"
                )


async def setup(bot):
    await bot.add_cog(Chance_Games(bot))