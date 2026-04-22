import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
from .Aviation_Utils.Aviation_Utils import send_hoppie_telex, get_metar, airport_lookup
from hoppie_connector import *
import os
import re
import asyncio
import aiosqlite
from datetime import datetime, timezone

# TODO:
# Implementation with metar command
# Allow for receiving messages
# Execute commands with receiving messages
# Implementation with flightplan command
# 
class Acars(commands.Cog):
    def __init__(self, bot, request_db, request_cursor):
        self.bot = bot
        self.logon = os.getenv("HOPPIE")
        self.connection:HoppieConnector = HoppieConnector(station_name="ORI", logon=self.logon)
        self.request_db:aiosqlite.Connection = request_db
        self.request_cursor:aiosqlite.Cursor = request_cursor

        self.telex_msgs = []

        # Begin polling task
        if not self.hoppie_polling.is_running():
            self.hoppie_polling.start()

    def get_time(self):
        return int(datetime.now(timezone.utc).timestamp())

        # Test command for sending messages
    @commands.command()
    async def send_telex(self, ctx:commands.Context, station, *, message):
        if ctx.author.id != 442728041115025410:
            await ctx.send("Command not available")
            return
        
        response = send_hoppie_telex(station, message)
        if response == True:
            await ctx.send("Message sent!")
        else:
            await ctx.send(f"Error: {response}")
    
    async def telex_metar(self, callsign, airport, time=None):
        metar = get_metar(airport)
        if time != None:
            # Check if it's a metar stop request
            if time == "S":
                # Make sure there is an entry to delete
                sql = "SELECT * FROM Requests WHERE callsign = ? AND airportICAO = ?"
                await self.request_cursor.execute(sql, (callsign, airport))
                result = await self.request_cursor.fetchone()
                if result is None:
                    await asyncio.sleep(15)
                    send_hoppie_telex(callsign, f"NO REQUESTS FOR {airport}")
                # Delete it
                sql = "DELETE FROM Requests WHERE callsign = ? AND airportICAO = ?"
                await self.request_cursor.execute(sql, (callsign, airport))
                await self.request_db.commit()
                return

            sql = "INSERT INTO Requests (userId, airportICAO, calls, nextCall, type, callsign) VALUES (?, ?, ?, ?, ?, ?)"
            await self.request_cursor.execute(sql, (0, airport, time, self.get_time() + 3600, "telex", callsign))
            await self.request_db.commit()
            await asyncio.sleep(15)
            send_hoppie_telex(callsign, f"{metar}\nSENDING METAR UPDATES FOR {time}H")
        else:
            await asyncio.sleep(15) # sleep 15 seconds, lowers load on hoppie
            send_hoppie_telex(callsign, metar)
    

    @tasks.loop(seconds=67)
    async def hoppie_polling(self):
        messages, delay = self.connection.poll()

        for msg in messages:
            print(f"FROM: {msg.get_from_name()}")
            print(f"TO: {msg.get_to_name()}")
            print(f"MSG: {msg.get_message()}")
            print("------")
            # Check if the message corresponds to any command
            # All commands must have 5 characters for the name. Worst case scenario a "." can be used to fill up space.
            # General conditions for these commands:
            # Bot will only answer when needed.
            # No answer either means the command doesn't exist. Or that it worked.
            pattern = "^([A-Z]{5})(.*)$"

            result = re.split(pattern, msg.get_message())

            if result != None:
                if len(result[1]) != 5:
                    print("failed check 2")
                    continue
                else:
                    result.pop(0)
            else:
                print("failed check 1")
                continue
            
            # Format was at least valid, now we check 
            # METAR: "METAR {ICAO} {hours}*     *optional. hours = S: stop metars for that airport"
            # TODO: Turn this into a function, alongside the rest of commands.
            if result[0] == "METAR":
                arguments = result[1].split() # [0] icao, [1] hours, optional

                if airport_lookup(arguments[0]) == False:
                    await asyncio.sleep(15)
                    send_hoppie_telex(msg.get_from_name(), f"{arguments[0]} NOT IN DATABASE")
                    continue

                if len(arguments) == 2:
                    await self.telex_metar(msg.get_from_name(), arguments[0], arguments[1])
                else:
                    await self.telex_metar(msg.get_from_name(), arguments[0])

            else:
                # Invalid command, do nothing
                print(f"failed check 3")
                continue

    @app_commands.command(name="acars_help", description="Shows ACARS functionality")
    async def acars_help(self, interaction:discord.Interaction):
        general_embed = discord.Embed(
            title="ACARS - Information",
            color=discord.Colour.gold(),
            description="Orion now has several functionality that can be accessed via ACARS. This embed features a list of these functions.\nOrion uses ORI as it's station\n" \
            "Note that functionality requires you to be using an aircraft compatible with Hoppie acars."
        )
        general_embed.set_thumbnail(url="https://i.redd.it/hx3hxf2gsnc31.png")
        general_embed.add_field(name="TELEX commands:", value=(
            "Telex commands consist of several functions to quickly ask for information such as metar reports, airport information or flightplan information.\n"
            "Make sure that you follow the format of the commands perfectly. Orion will NOT respond to commands that don't follow the format properly.\n"
            "In addition, Orion can take between 15 seconds to 2 minutes to respond to messages. This has been done in order to not strain the HOPPIE network"
        ), inline=False)

        general_embed.set_footer(text="Orion uses Hoppie:https://www.hoppie.nl/")


        telex_embed = discord.Embed(
            title="TELEX - Information",
            color=discord.Color.gold(),
            description="This embed shows all available commands that can be executed via telex. Please make sure to follow the correct format. Blank spaces are also required"
        )
        telex_embed.add_field(name="METAR: Format: `METAR {airport_icao} HOURS`", value=(
            "This command is extremely similar to /metar_request. When used it will return the current metar for the airport.\n"
            "In addition, you can queue up updates with optional HOURS field. You'll recieve a metar for every hour that passes until the time assigned has passed.\n"
            "If you wish to cancel a queue, send the same command but with an S on the hours. This will cancel the request. Do note that a sucessful execution will not send a response back"
        ))
        telex_embed.set_footer(text="Orion uses Hoppie:https://www.hoppie.nl/")

        embeds = [general_embed, telex_embed]

        class AcarsView(discord.ui.View): # 
            def __init__(self, embed):
                super().__init__()
                self.embeds = embeds

            @discord.ui.select(
                placeholder = "Select an option:",
                min_values = 1,
                max_values = 1,
                options = [
                    discord.SelectOption(
                        label = "ACARS - Information",
                        description= "Shows general information",
                        emoji = "📝"
                    ),
                    discord.SelectOption(
                        label = "TELEX - Information",
                        description = "Shows information about telex commands",
                        emoji = "💬"
                    )
                ]
            )
            async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                index = ["ACARS - Information", "TELEX - Information"].index(select.values[0])
                await interaction.response.edit_message(embed=self.embeds[index], view=self)
        
        await interaction.response.send_message(view=AcarsView(embeds), embed=general_embed)




async def setup(bot):
    db_requests_path = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "requests.db")
    db = await aiosqlite.connect(db_requests_path)
    cursor = await db.cursor()
    await bot.add_cog(Acars(bot, db, cursor))