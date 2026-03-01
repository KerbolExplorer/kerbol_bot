import discord
from discord import app_commands
from discord.ext import commands

class Mods(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=["lc"])
    async def lethal(self, ctx : commands.Context):
        guild_id = ctx.guild.id
        if guild_id == 671398463287722006:
            string = """**ACTUALIZADO EL 1/3/2026**\nLauncher de mods:https://thunderstore.io/package/ebkr/r2modman/\nCodigo:`019caa76-9ea6-9504-3486-6c9d04b19cb4`\nComo usar: Instala r2modman por el enlace manual, una vez instalado en tu pc busca Lethal Company en la lista de juegos y pincha en 'Import/Update'.Dale a importar con codigo, introduce el codigo para el modpack y descargalos. Una vez hecho clickea en el perfil del modpack y seleciona 'Launch modded'.Con esto se iniciara el juego. Es normal que tarde un rato en iniciarse. Con todo esto hecho ya deberias estar listo para jugar!\n-# En el caso de que el codigo este desactualizado, avisen a Kerbol"""
            await ctx.send(string)
        else:
            await ctx.send("This server does not have any modding instructions for this game. Please contact Kerbol to add them")
    
    @commands.command(aliases=["Left4Dead2"])
    async def l4d2(self, ctx : commands.Context):
        guild_id = ctx.guild.id
        if guild_id == 671398463287722006:
            string = """**ACTUALIZADO EL 1/7/2025**\nLink a lista de mods:https://steamcommunity.com/sharedfiles/filedetails/?id=3391726295 (La lista de mods es privada, tienes q ser amigo de espejismo para poder accederla)\n\nComo usar: Abre el enlace en steam, y clikea en subscribirse a todos. Una vez descargado los mods, abre l4d2 y comprobaras que en el menu principal, hay un circulo rojo al lado de 'ADDONS' ESPERA A QUE EL CIRCULO SE VAYA. Si no los mods no se cargaran y no apareceran el la partida. Para activar los mods entra en addons y tendras la lista de mods instalados. Simplemente cliquea en los mods para activarlos. Debido a que hay varios mods que cambian al mismo personaje, no puedes simplemente activar toda la lista, asi que configura los mods como sean necesarios en esta sesión.\n-# En el caso de que el codigo este desactualizado, avisen a Kerbol"""
            await ctx.send(string)
        else:
            await ctx.send("This server does not have any modding instructions for this game. Please contact Kerbol to add them")

async def setup(bot):
    await bot.add_cog(Mods(bot))