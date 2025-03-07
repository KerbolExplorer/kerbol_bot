import discord
from discord import app_commands
from discord.ext import commands
import random

class rps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="rockpaperscissors",description="Play rock paper scissors")
    async def rockpaperscissors(self, interaction:discord.Interaction):
        bot_play = random.randint(0, 2)         #grab a number from 0 to 2, 0 = rock, 1 = scissors, 2 = paper

        player = interaction.user.id

        #class to store the buttons + responses
        class Buttons(discord.ui.View):
            def __init__(self, bot_play, *, timeout = 180):
                super().__init__(timeout=timeout)
                self.bot_play = bot_play
        

            @discord.ui.button(label="🪨", style=discord.ButtonStyle.blurple)
            async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != player:
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send("You need to be the one that started the game to do this", ephemeral=True)
                    return
                button.style = discord.ButtonStyle.success
                await self.disable_buttons(self, interaction)
                await interaction.response.edit_message(view=self)
                if bot_play == 0:
                    await interaction.followup.send("Piedra!, empate")
                elif bot_play == 1:
                    await interaction.followup.send("Tijeras...perdi")
                else:
                    await interaction.followup.send("Papel! Gane!")
        
            @discord.ui.button(label="✂️", style=discord.ButtonStyle.blurple)
            async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != player:
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send("You need to be the one that started the game to do this", ephemeral=True)
                    return
                button.style = discord.ButtonStyle.success
                await self.disable_buttons(self, interaction)
                await interaction.response.edit_message(view=self)
                if bot_play == 0:
                    await interaction.followup.send("Piedra! Gane!")
                elif bot_play == 1:
                    await interaction.followup.send("Tijeras, empate")
                else:
                    await interaction.followup.send("Papel!...perdi")
        
            @discord.ui.button(label="🗞️", style=discord.ButtonStyle.blurple)
            async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != player:
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send("You need to be the one that started the game to do this", ephemeral=True)
                    return
                button.style = discord.ButtonStyle.success
                await self.disable_buttons(self, interaction)
                await interaction.response.edit_message(view=self)
                if bot_play == 0:
                    await interaction.followup.send("Piedra!..perdi")
                elif bot_play == 1:
                    await interaction.followup.send("Tijeras! Gane!")
                else:
                    await interaction.followup.send("Papel, empate")
        
            async def disable_buttons(self, child:discord.ui.Button, interaction: discord.Interaction):
                for child in self.children:
                    child.disabled = True

    
        await interaction.response.send_message("Haz tu jugada", view=Buttons(bot_play))
    
async def setup(bot): 
    await bot.add_cog(rps(bot))