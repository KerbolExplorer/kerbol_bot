import discord
from discord.ext import commands
import asyncio
import random

from bot_data import give_token
token = give_token()

bot = commands.Bot(command_prefix="S!", intents=discord.Intents.all())

async def change_activity():
    gameList = (
        "Persona 3 FES", "Persona 3 Reload", "Persona 4 Golden", "Persona 5 Royal", "Pokemon Sun", 
        "Pokemon Mystery Dungeon: Explorers of Sky", "Pokemon Super Mystery Dungeon", "Subnautica",
        "Subnautica: Below Zero", "Microsoft Flight Simulator 2024", "Terraria", "No Mans Sky", "Celeste",
        "The Elder Scrolls V: Skyrim", "Halo: The Master Chief Collection", "Halo Infinite", "Ace Combat 7: Skies Unknown",
        "Project Wingman", "Rivals of Aether", "Deep Rock Galactic", "FalconBMS", "Enter the Gungeon", "FTL: Faster Than Light", 
        "Pokerogue", "Monster Hunter Wilds", "Kerbal Space Program", "Team Fortess 2", "Metal Gear Rising: Revengance", "Starbound", 
        "Sea of Stars", "Miitopia", "Slime Rancher", "Marvel Rivals", "Hollow Knight", "Hollow Knight: Zote boat", "Fortnite", "Amorous",
        "Ad Astra", "Metaphor: Refantazio", "Lethal Company"
        )
    
    while True:
        chosen_game = random.randint(0, (len(gameList) -1))
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(gameList[chosen_game]))
        await asyncio.sleep(10800)

@bot.event
async def on_ready():
    print("Ready to dance!")
    bot.loop.create_task(change_activity())

    cogs_list_Test_Commands = ['Cogs.Test_Commands.Ping']
    cogs_list_dev = ['Cogs.Dev_Only.Run','Cogs.Dev_Only.Say']
    cogs_list_lvl = ['Cogs.Level_System.Level_System', 'Cogs.Level_System.Level', 'Cogs.Level_System.Profile', 'Cogs.Level_System.Leaderboard']
    cogs_list_games = ['Cogs.Games.rps']
    cogs_list_aviation = ['Cogs.Aviation.Airport_Lookup', 'Cogs.Aviation.Airline_Manager', 'Cogs.Aviation.Schedule', 'Cogs.Aviation.Metar']
    cogs_list_music = ['Cogs.Music.Music']
    cogs_list_misc = ['Cogs.Misc.Bite', 'Cogs.Misc.Pet', 'Cogs.Misc.Fetch', 'Cogs.Misc.About', 'Cogs.Misc.Responses']

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
    
    for cog in cogs_list_music:
        await bot.load_extension(cog)
    
    for cog in cogs_list_misc:
        await bot.load_extension(cog)

    print("Cogs loaded!")

    await bot.tree.sync()
    print("Sync has been successful")


bot.run(token)