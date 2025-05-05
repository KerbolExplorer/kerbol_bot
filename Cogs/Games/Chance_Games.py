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

        MAX_DICES = 10000
        MAX_DISPLAY = 50

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
            if dices <= MAX_DISPLAY:
                current_dice = 1
                total_dices = []
                while current_dice <= dices:
                    result = random.randint(1, sides)
                    total_dices.append(result)
                    current_dice += 1
                total = 0
                for dice in total_dices:
                    total += dice
                string = f"The dices roll as follow: {total_dices}\n"
            elif dices > MAX_DICES:
                await interaction.response.send_message(f"Yeah no those are way too many dices, please do something less than {MAX_DICES}", ephemeral=True)
                return
            else:
                string = f"You are asking for too many dices, so I can't show you what each dice rolls, you'll have to trust me on this one.\n"
                total = 0
                for _ in range(dices):
                    total += random.randint(1, sides)
            if len(string) > 2000:
                string = f"I can't tell you what each dices has rolled because of the message character limit, so you'll have to trust me on this one\n"
            if total == 69 or total == 420 or total == 621:
                string += f"They all add up to **{total}**, heh nice"
            else:
                string += f"They all add up to **{total}**"

            await interaction.response.send_message(string)
    
    @app_commands.command(name="8ball", description="Ask a question to an 8ball")
    @app_commands.describe(question="The question you want to ask")
    async def eight_ball(self, interaction:discord.Interaction, question:str):
        responses = (
            "It is certain", "It is decidly so", "Without a doubt", "Yes definitely", "You may rely on it", "As I see it, yes", "Most likely",
            "Outlook good", "Yes", "Signs point to yes", "Hmmmmm", "Reply hazy, try again", "Ask again later", "Better not tell you now",
            "Cannot predict now", "Concentrate and ask again", "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
            "Very doubtful"
            )
        response = random.choice(responses)
        await interaction.response.send_message(f"Question: {question}\nAnswer: {response}")


async def setup(bot):
    await bot.add_cog(Chance_Games(bot))