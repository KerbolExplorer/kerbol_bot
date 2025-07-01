import discord
from discord import app_commands
from discord.ext import commands

class Mods(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def lethal(self, ctx : commands.Context):
        guild_id = ctx.guild.id
        if guild_id == 671398463287722006:
            string = """**ACTUALIZADO EL 1/7/2025**\nLauncher de mods:https://thunderstore.io/package/ebkr/r2modman/\nCodigo:`0197c17b-4420-113b-e204-6c6b8b913f2d`\nComo usar: Instala r2modman por el enlace manual, una vez instalado en tu pc busca Lethal Company en la lista de juegos y pincha en 'Import/Update'.Dale a importar con codigo, introduce el codigo para el modpack y descargalos. Una vez hecho clickea en el perfil del modpack y seleciona 'Launch modded'.Con esto se iniciara el juego. Es normal que tarde un rato en iniciarse. Con todo esto hecho ya deberias estar listo para jugar!\n-# En el caso de que el codigo este desactualizado, avisen a Kerbol"""
            await ctx.send(string)
        else:
            await ctx.send("This server does not have any modding instructions for this game. Please contact Kerbol to add them")


async def setup(bot):
    await bot.add_cog(Mods(bot))