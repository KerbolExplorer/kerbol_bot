import discord
from discord.ext import commands, tasks
import asyncio
import random
import traceback
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

#from bot_data import give_token
token = os.getenv("TOKEN")
admin = os.getenv("ADMIN")

bot = commands.Bot(command_prefix="S!", intents=discord.Intents.all())

async def change_activity():
    gameList = (
        "Persona 3 FES", "Persona 3 Reload", "Persona 4 Golden", "Persona 5 Royal", "Pokemon Sun", 
        "Pokemon Mystery Dungeon: Explorers of Sky", "Pokemon Super Mystery Dungeon", "Subnautica",
        "Subnautica: Below Zero", "Microsoft Flight Simulator 2024", "Terraria", "No Mans Sky", "Celeste",
        "The Elder Scrolls V: Skyrim", "Halo: The Master Chief Collection", "Halo Infinite", "Ace Combat 7: Skies Unknown",
        "Project Wingman", "Rivals of Aether", "Deep Rock Galactic", "FalconBMS", "Enter the Gungeon", "FTL: Faster Than Light", 
        "Pokerogue", "Monster Hunter Wilds", "Kerbal Space Program", "Team Fortess 2", "Metal Gear Rising: Revengance", "Starbound", 
        "Sea of Stars", "Miitopia", "Slime Rancher", "Marvel Rivals", "Hollow Knight", "Hollow Knight: Zoteboat", "Fortnite", "Amorous",
        "Ad Astra", "Metaphor: Refantazio", "Lethal Company", "Devil May Cry 5", "Tomodatchi Life", "Frostpunk", "Xplane 12", "Balatro", 
        "The Elder Scrolls IV: Oblivion", "Pokken Tournament DX", "Super Smash Bros. Ultimate"
        )
    
    while True:
        chosen_game = random.randint(0, (len(gameList) -1))
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(gameList[chosen_game]))
        await asyncio.sleep(10800)

@bot.event
async def on_ready():
    bot.loop.create_task(change_activity())

    cogs_list_Test_Commands = ('Cogs.Test_Commands.Ping',)
    cogs_list_dev = ('Cogs.Dev_Only.Run','Cogs.Dev_Only.Say', 'Cogs.Dev_Only.Dev_commands')
    cogs_list_lvl = ('Cogs.Level_System.Level_System', 'Cogs.Level_System.Level', 'Cogs.Level_System.Profile', 'Cogs.Level_System.Leaderboard')
    cogs_list_games = ('Cogs.Games.rps', 'Cogs.Games.Chance_Games', 'Cogs.Games.Gunslingers')
    cogs_list_aviation = ('Cogs.Aviation.Airport_Lookup', 'Cogs.Aviation.Airline_Manager', 'Cogs.Aviation.Schedule', 'Cogs.Aviation.Metar')
    cogs_list_util = ('Cogs.Util.Server', 'Cogs.Util.About', 'Cogs.Util.Reminder')
    cogs_list_misc = ('Cogs.Misc.Bite', 'Cogs.Misc.Pet', 'Cogs.Misc.Fetch', 'Cogs.Misc.Responses', 'Cogs.Misc.Rate')

    for cog in cogs_list_Test_Commands:
        await bot.load_extension(cog)
    
    for cog in cogs_list_dev:
        await bot.load_extension(cog)
    
    for cog in cogs_list_lvl:
        await bot.load_extension(cog)
    
    for cog in cogs_list_games:
        await bot.load_extension(cog)
    
    for cog in cogs_list_aviation:
        await bot.load_extension(cog)
    
    for cog in cogs_list_util:
        await bot.load_extension(cog)
    
    for cog in cogs_list_misc:
        await bot.load_extension(cog)

    print("Cogs loaded!")

    await bot.tree.sync()
    print("Sync has been successful")
    print("Ready to dance!")

    if not morning_call.is_running():
        morning_call.start()

@tasks.loop(minutes=60)
async def morning_call():
    target_time = "07Z"
    current_time = datetime.now(timezone.utc)
    current_time = current_time.strftime("%HZ")
    admin_user = await bot.fetch_user(admin)
    if current_time == target_time:
        greetings = (
            "Morning bud!", "Morning!", "Morning snack~", "Hey hey!", "Morning, I require headpats", "Morning!, slept well?", "Morning!, I hope you have a nice day!"
            )
        chosen_greeting = random.randint(0, (len(greetings) -1))
        await admin_user.send(greetings[chosen_greeting])

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if interaction.command == None:
        await interaction.response.send_message(f"This command is temporarely disabled", ephemeral=True)
        return

    admin_user = await bot.fetch_user(admin)
    await admin_user.send(
        f"Hey, an error has ocurred while executing `{interaction.command.name}`\n"
        f"Type: `{type(error).__name__}`\n"
        f"Message: `{str(error)}`"
                        )
    try:
        await interaction.response.send_message(f"Something went wrong while doing this command, I have notified {admin_user.display_name} about it", ephemeral=True)
    except discord.InteractionResponded:
        await interaction.followup.send(f"Something went wrong while doing this command, I have notified {admin_user.display_name} about it", ephemeral=True)

    print(f"\nException occurred in command: {interaction.command.name}")
    traceback.print_exception(type(error), error, error.__traceback__)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

bot.run(token)