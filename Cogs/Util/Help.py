import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Shows information about Orion's commands")
    async def help(self, interaction:discord.Interaction):
        init_embed = discord.Embed(
            title="Orion bot, Help command",
            color=discord.Colour.gold(),
            description="This commands shows information of several commands belonging to the bot, choose one of the categories below to read on the commands.\n" \
            "In addition, Orion has other hidden commands that can be accessed with the prefix S!. This commands are usually secrets or meant for debugging."
        )


        av_embed = discord.Embed(
            title="Aviation commands",
            color=discord.Colour.gold(),
            description="Information of the commands belonging to the Aviation category"
        )
        av_embed.add_field(name="airport", value="Gives general information about an airport, requires an icao code to be passed through.")
        av_embed.add_field(name="airport-distance", value="Returns the distance between two airports in nm.")
        av_embed.add_field(name="metar", value="Gives the metar of an airport alongside a summary in an easier to read manner.")
        av_embed.add_field(name="metar_request", value="Allows for Orion to DM you the metar for the chosen airport along the specified amount of time.")
        av_embed.add_field(name="metar_stop", value="Cancels a metar request.")
        av_embed.add_field(name="metar_list", value="Lists the metar request you currently have.")
        av_embed.add_field(name="zulu_time", value="Shows the current zulu time.")
        av_embed.add_field(name="bare_converter", value="Converts barometric pressures.")
        av_embed.add_field(name="temp_converter", value="Converts a value to either celcius or farenheith")
        av_embed.add_field(name="random_regional_flight", value="Returns a random flight between two airports depending on the parameters given")
        av_embed.add_field(name="Flightplan", value="Provides a summary of the latest simbrief flightplan.")

        games_embed = discord.Embed(
            title="Game Commands",
            color=discord.Colour.gold(),
            description="Information about commands belonging to the Games category"
        )

        games_embed.add_field(name="coinflip", value="Does a coinflip")
        games_embed.add_field(name="diceroll", value="Provides a diceroll, can be configured as needed")
        games_embed.add_field(name="8ball", value="Ask a question to a magical 8ball and get an answer back, most of the time")
        games_embed.add_field(name="gunslingers", value="Play a game of gunslingers")
        games_embed.add_field(name="gunslingers-about", value="Shows information about gunslingers")
        games_embed.add_field(name="rockpaperscissors", value="Play a game of rps against Orion")
        games_embed.add_field(name="pokemon", value="Shows information about a chosen pokemon.")

        profile_embed = discord.Embed(
            title="Profile Commands",
            color=discord.Colour.gold(),
            description="Information about profile related commands"
        )
        profile_embed.add_field(name="leaderboard", value="Shows the server leaderboard")
        profile_embed.add_field(name="level", value="Shows your current level")
        profile_embed.add_field(name="profile", value="Shows your profile")
        profile_embed.add_field(name="banner", value="Shows a user's banner")

        misc_embed = discord.Embed(
            title="Misc. commands",
            color=discord.Colour.gold(),
            description="Information about misc. commands"
        )

        misc_embed.add_field(name="bite", value="Send Orion to bite someone")
        misc_embed.add_field(name="fetch", value="Play fetch with Orion")
        misc_embed.add_field(name="pet", value="Pet Orion uwu")
        misc_embed.add_field(name="rate", value="Have Orion rate something")

        util_embed = discord.Embed(
            title="Utility Commands",
            color=discord.Colour.gold(),
            description="Information about utility Commands"
        )
        util_embed.add_field(name="about", value="Shows general information about Orion")
        util_embed.add_field(name="help", value="You are not going to believe this")
        util_embed.add_field(name="remindme", value="Set up a reminder for a future date, Orion will DM you on set date")
        util_embed.add_field(name="quick-remind", value="Set up a quick reminder, Orion will dm you in x seconds")
        util_embed.add_field(name="remind_list", value="Shows a list of your current reminders")
        util_embed.add_field(name="remind_cancel", value="Cancels a reminder")
        util_embed.add_field(name="say", value="Have Orion say something")
        util_embed.add_field(name="set_reaction_role", value="[REQUIRES MANAGE ROLE PERMS] Allows to set up a role reaction on one of Orion's messages")
        util_embed.add_field(name="remove_reaction_role", value="[REQUIRES MANAGE ROLE PERMS] Removes a reaction role")
        util_embed.add_field(name="server", value="Shows information about the server")
        util_embed.add_field(name="enable_custom_role", value="[REQUIRES MANAGE ROLE PERMS] Enables custom roles on this server. Existing roles must be linked with the S!sync command and contain the word 'unlinked' on them. Each custom role is limited to 1 user")
        util_embed.add_field(name="custom_role", value="Creates, Edits and Deletes custom roles")
        


        embeds = [init_embed, av_embed, games_embed, profile_embed, misc_embed, util_embed]

        class HelpView(discord.ui.View):         # select 0 = General, select 1 = Fleet, select 2 = hubs, select 3 = schedules, select 4 = Economy
            def __init__(self, embeds):
                super().__init__()
                self.embeds = embeds
            
            @discord.ui.select(
                placeholder = "Select an option:",
                min_values = 1,
                max_values = 1,
                options = [
                    discord.SelectOption(
                        label = "General Information",
                        description= "Shows general information",
                        emoji = "📝"
                    ),
                    discord.SelectOption(
                        label = "Aviation",
                        description = "Shows information about aviation commands",
                        emoji = "✈️"
                    ),
                    discord.SelectOption(
                        label= "Games",
                        description = "Shows information about game commands",
                        emoji = "🎮"
                    ),
                    discord.SelectOption(
                        label = "Profile",
                        description = "Shows information about profile commands",
                        emoji = "🫵"
                    ),
                    discord.SelectOption(
                        label = "Misc",
                        description = "Shows information about misc. commands",
                        emoji = "🗯️"
                    ),
                    discord.SelectOption(
                        label = "Utility",
                        description = "Shows information about utility commands",
                        emoji = "🔧"
                    )
                ]
            )
            async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                index = ["General Information", "Aviation", "Games", "Profile", "Misc", "Utility"].index(select.values[0])
                await interaction.response.edit_message(embed=self.embeds[index], view=self)
        
        await interaction.response.send_message(view=HelpView(embeds), embed=init_embed)
    
        

async def setup(bot):
    await bot.add_cog(Help(bot))