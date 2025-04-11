import discord
from discord import app_commands
from discord.ext import commands
import io
import contextlib

class Run(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="run", description="[DEV ONLY COMMAND], runs whatever text was given and returns the result")
    @app_commands.describe(
        script="The code Solgaleo will execute"
    )
    async def run(self, interaction:discord.Interaction, script: str):
        if interaction.user.id != 442728041115025410:
            await interaction.response.send_message("Only Kerbol can use this command!", ephemeral=True)
            return
        
        output_stream = io.StringIO()

        with contextlib.redirect_stdout(output_stream):
            try:
                exec(script)
            except Exception as e:
                await interaction.response.send_message(f"An error has occured: {e}")
                return
        
        output = output_stream.getvalue().strip()

        if not output:
            output = "No output returned."

        await interaction.response.send_message(f"```{output}```")


async def setup(bot): # this is called by Pycord to setup the cog
    await bot.add_cog(Run(bot)) # add the cog to the bot
