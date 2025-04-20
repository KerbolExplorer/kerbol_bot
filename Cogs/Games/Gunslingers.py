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
    @app_commands.describe(difficulty="Int represting the difficulty of the bot, more info in gunslinger-about")
    async def gunslingers(self, interaction:discord.Interaction, difficulty:int = 2):
        if difficulty < 1 or difficulty > 3:
            await interaction.response.send_message("Difficulty must either be 1, 2 or 3")
            return
        class Buttons(discord.ui.View):
            def __init__(self, *, timeout = 180):
                super().__init__(timeout=timeout)
            
            @discord.ui.button(label="🔫", style=discord.ButtonStyle.blurple)
            async def shoot(self, interaction:discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer(ephemeral=True)
                if interaction.user.id == player1.id:
                    player1.choice = "Shoot"
                else:
                    await interaction.followup.send("You are not participating in this game", ephemeral=True)

            @discord.ui.button(label="🔄️", style=discord.ButtonStyle.blurple)
            async def reload(self, interaction:discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer(ephemeral=True)
                if interaction.user.id == player1.id:
                    player1.choice = "Reload"
                else:
                    await interaction.followup.send("You are not participating in this game", ephemeral=True)

            @discord.ui.button(label="🛡️", style=discord.ButtonStyle.blurple)
            async def shield(self, interaction:discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer(ephemeral=True)
                if interaction.user.id == player1.id:
                    player1.choice = "Shield"
                else:
                    await interaction.followup.send("You are not participating in this game", ephemeral=True)


        current_turn = 0
        embed = discord.Embed(
        color=0xf1c40f,
        title=f"Gunslingers",
        description="Choose one of the 3 actions"
        )
        embed.set_footer(text=f"Playing at difficulty {difficulty}")

        if difficulty == 1:
            await interaction.response.send_message("I guess I can let a dice play for me")
        elif difficulty == 2:
            await interaction.response.send_message("Alright I'll go easy on ya")
        else:
            await interaction.response.send_message("Ok, let's see what you got")
        view = Buttons()
        message = await interaction.followup.send(view=view, embed=embed, wait=True)
        player1 = await self.Player(interaction.user.id, self.bot).init()
        player2 = await self.Player(self.bot.user.id, self.bot).init()

        last_opponent_choice = None

        opponent_ammo = 0
        opponent_history = []
        bot_history = []
        
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
            if difficulty == 1:
                choices = ("Shield", "Shoot", "Reload")
                player2.choice = choices[random.randint(0, (len(choices) - 1))]
                if current_turn == 0:
                    player2.choice = "Reload"
            elif difficulty == 2:
                if player2.ammo == 0:
                    if last_opponent_choice == "Reload":
                        player2.choice = random.choice(("Reload", "Reload", "Shield"))
                    else:
                        player2.choice = "Reload"
                elif last_opponent_choice == "Reload" and player2.ammo > 0:
                    player2.choice = "Shield"
                elif last_opponent_choice == "Shoot":
                    player2.choice = "Shoot"
                elif last_opponent_choice == "Shield":
                    player2.choice = random.choice(("Shield", "Shield", "Reload"))
                else:
                    player2.choice = random.choice(("Shoot", "Reload", "Shield"))
            else:
                weights = {"Shoot": 1, "Shield": 1, "Reload": 1}
                
                if player2.ammo == 0:
                    if opponent_ammo == 0:          #If the opponent has no ammo we reload normally
                        weights["Reload"] = 1000    
                    else:                           #If the opponent has ammo, expect a shot
                         weights["Shield"] += 4    

                if opponent_history.count("Reload") > opponent_history.count("Shoot"):  #If the opponent likes to reload, shoot him
                    weights["Shoot"] += 2

                if opponent_history.count("Shoot") > opponent_history.count("Reload"):  #If the opponent is aggressive, play defensive
                    weights["Shield"] += 2

                if len(opponent_history) >= 3 and opponent_history[-3:] == ["Shield", "Reload", "Shield"]:  #Detect baiting
                    weights["Shoot"] += 2

                if len(opponent_history) >= 2 and opponent_history[-1] == opponent_history[-2]:
                    weights[last_opponent_choice] -= 1  # Anticipate switch-up

                if last_opponent_choice == "Shield" and opponent_ammo > 0:
                    weights["Shield"] += 2              # If the player has ammo and just shielded, a shot is likely

                if opponent_history.count("Shield") >= 2:
                    weights["Reload"] += 1                   #Stall detection (shield spam)
            
                if random.random() < 0.1:
                    weights["Shield"] += 1

                if opponent_ammo > 0:
                    weights["Shield"] += 2
            
                if current_turn > 5:
                    weights["Shoot"] += 1
                
                if player2.ammo >= 2:
                    weights["Shoot"] += 1    #Go aggressive when we have plenty of bullets
                elif player2.ammo == 1 and opponent_ammo == 0:
                    weights["Shoot"] += 2    #If the opponent doesn't have bullets we can just shoot lol

                #Try to predict what the opponent will do
                if len(opponent_history) >= 2:
                    if opponent_history[-1] == opponent_history[-2]:
                        likely_next = "Shoot" if last_opponent_choice != "Shoot" else "Reload"
                        weights[likely_next] += 1

                if len(bot_history) >= 2 and bot_history[-1] == bot_history[-2]:
                    weights[bot_history[-1]] -= 1  # encourage variation
                
            
                for k in weights:
                    weights[k] = max(weights[k], 0)

                choices = []
                for move, weight in weights.items():
                    choices.extend([move] * weight)
            
                player2.choice = random.choice(choices)

                if current_turn == 0:
                    player2.choice = "Reload"       #At turn 0, the sensible thing to do, is to reload
                elif current_turn == 1:
                    player2.choice = "Shield"       #Shield just incase the player shoots the second he has a bullet

                if player2.choice == "Shoot" and player2.ammo == 0:
                    player2.choice = random.choice(("Reload", "Shield")) #Last ditch effort to avoid an empty shot
        
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

            last_opponent_choice = player1.choice
            opponent_history.append(player1.choice)
            bot_history.append(player2.choice)

            if player1.choice == "Reload":
                opponent_ammo += 1
            elif player1.choice == "Shoot":
                opponent_ammo -= 1

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
            color=0xf1c40f,
            description="Gunslingers is a two player game, currently only allowing for player vs bot, players must try to take down their opponent with the use of 3 actions"
                              )
        embed.add_field(name="Shoot 🔫", value="Shoots the opponent, as long as you have ammo and they aren't shielding. If the attack succeeds, you win.")
        embed.add_field(name="Reload 🔄️", value="Adds a bullet to your bullet count. Both players start with 0 bullets.")
        embed.add_field(name="Shield 🛡️", value="Shields yourself from an upcoming attack. You'll survive the hit and the bullet will be wasted")
        embed.add_field(name="Bot difficulty: ", value=
                        "The difficulty the bot will be playing at.\n\n"
                        "**Difficulty 1**: Solgaleo will simply choose his moves randomly.\n"
                        "**Difficulty 2**: Solgaleo keeps track of his bullets and the last turn of his opponent.\n"
                        "**Difficulty 3**: Solgaleo will track his opponets behavior and bullets over multiple turns."
        "")
        embed.set_footer(text="At no difficulty does Solgaleo read the current player action")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Gunslingers(bot))