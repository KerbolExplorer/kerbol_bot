import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

class Gunslingers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class Player:
        def __init__(self, id, bot):
            self.bot = bot
            self.ammo = 0
            self.shielded = False
            self.choice = ""
            self.alive = True
            self.id = id
            self.name = None

        async def init(self):
            user = await self.bot.fetch_user(self.id)
            self.name = user.display_name
            return self

    @app_commands.command(name="gunslingers", description="Play a game of Gunslingers against Solgaleo")
    async def gunslingers(self, interaction:discord.Interaction):

        class Buttons(discord.ui.View):
            def __init__(self, *, timeout = 180):
                super().__init__(timeout=timeout)
            
            @discord.ui.button(label="🔫", style=discord.ButtonStyle.blurple)
            async def shoot(self, interaction:discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer(ephemeral=True)
                if interaction.user.id == player1.id:
                    player1.choice = "Shoot"
                    await interaction.followup.send("Action chosen!", ephemeral=True)
                else:
                    await interaction.followup.send("You are not participating in this game", ephemeral=True)

            @discord.ui.button(label="🔄️", style=discord.ButtonStyle.blurple)
            async def reload(self, interaction:discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer(ephemeral=True)
                if interaction.user.id == player1.id:
                    player1.choice = "Reload"
                    await interaction.followup.send("Action chosen!", ephemeral=True)
                else:
                    await interaction.followup.send("You are not participating in this game", ephemeral=True)

            @discord.ui.button(label="🛡️", style=discord.ButtonStyle.blurple)
            async def shield(self, interaction:discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer(ephemeral=True)
                if interaction.user.id == player1.id:
                    player1.choice = "Shield"
                    await interaction.followup.send("Action chosen!", ephemeral=True)
                else:
                    await interaction.followup.send("You are not participating in this game", ephemeral=True)


        current_turn = 0
        embed = discord.Embed(
        color=self.bot.user.accent_color,
        title=f"Gunslingers",
        description="Choose one of the 3 actions"
        )

        await interaction.response.send_message("Commencing a gunslingers game...")
        view = Buttons()
        message = await interaction.followup.send(view=view, embed=embed, wait=True)
        player1 = await self.Player(interaction.user.id, self.bot).init()
        player2 = await self.Player(self.bot.user.id, self.bot).init()

        
        while player1.alive and player2.alive:
            view = Buttons()
            await message.edit(embed=embed, view=view)
            
            wait_time = 30
            elapsed = 0
            interval = 1

            while player1.choice == "" and elapsed < wait_time:
                await asyncio.sleep(interval)
                elapsed += interval
    
            if player1.choice == "":
                await interaction.followup.send("You took too long to respond! Game over")
                break
            
            #Bot logic
            choices = ("Shield", "Shoot", "Reload")
            player2.choice = choices[random.randint(0, (len(choices) - 1))]
            if current_turn == 0:
                player2.choice = "Reload"

            turn_result = []
            turn_result.append(f"**TURN {current_turn} RESULTS**")
            turn_result.append(f"{player1.name} chooses **{player1.choice}**")
            turn_result.append(f"{player2.name} chooses **{player2.choice}**")

            if player1.choice == "Shield":
                player1.shielded = True
                turn_result.append(f"{player1.name} shields themselves.")
            if player2.choice == "Shield":
                player2.shielded = True
                turn_result.append(f"{player2.name} shields themselves.")


            if player1.choice == "Shoot":
                if player1.ammo <= 0:
                    turn_result.append(f"{player1.name} tries to shoot, but has no bullets!")
                elif player2.shielded:
                    player1.ammo -= 1
                    turn_result.append(f"{player1.name} shoots, but {player2.name} blocks it!")
                else:
                    player1.ammo -= 1
                    player2.alive = False
                    turn_result.append(f"{player1.name} shoots and takes down {player2.name}!")
            elif player1.choice == "Reload":
                player1.ammo += 1
                turn_result.append(f"{player1.name} reloads.")


            if player2.choice == "Shoot":
                if player2.ammo <= 0:
                    turn_result.append(f"{player2.name} tries to shoot, but has no bullets!")
                elif player1.shielded:
                    player2.ammo -= 1
                    turn_result.append(f"{player2.name} shoots, but {player1.name} blocks it!")
                else:
                    player2.ammo -= 1
                    player1.alive = False
                    turn_result.append(f"{player2.name} shoots and takes down {player1.name}!")
            elif player2.choice == "Reload":
                player2.ammo += 1
                turn_result.append(f"{player2.name} reloads.")
            
            embed.description= "\n".join(turn_result)
        
            player1.choice = ""
            player2.choice = ""    
            player1.shielded = False
            player2.shielded = False

            current_turn += 1
        
        view = Buttons()
        for child in view.children:
            child.disabled = True

        await message.edit(embed=embed, view=view)

        if player1.alive and player2.alive == False:
            await interaction.followup.send(f"{player1.name} wins!")
        elif player1.alive == False and player2.alive == True:
            await interaction.followup.send(f"{player2.name} wins!")
        elif player1.alive == False and player2.alive == False:
            await interaction.followup.send("The two players have been KO'd it's a tie")
    
    @app_commands.command(name="gunslingers-about", description="General info about gunslingers")
    async def about(self, interaction:discord.Interaction):
        embed = discord.Embed(
            title="Gunslingers",
            description="Gunslingers is a two player game, currently only allowing for player vs bot, players must try to take down their opponent with the use of 3 actions"
                              )
        embed.add_field(name="Shoot 🔫", value="Shoots the opponent, as long as you have ammo and they aren't shielding. If the attack succeeds, you win.")
        embed.add_field(name="Reload 🔄️", value="Adds a bullet to your bullet count. Both players start with 0 bullets.")
        embed.add_field(name="Shield 🛡️", value="Shields yourself from an upcoming attack. You'll survive the hit and the bullet will be wasted")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Gunslingers(bot))