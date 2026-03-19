import discord
from discord import app_commands
from discord.ext import commands
import requests
from dataclasses import dataclass
import json
import random

class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @dataclass
    class Pokemon_data:
        name:str
        number:int
        description:str
        height:str
        color:str
        weight:str

        abilites:dict
        types:tuple
        hp:int
        attack:int
        defense:int
        sp_attack:int
        sp_defense:int
        speed:int

        is_shiny:bool

        egg_group:list
        tier:str

        pre_evolutions:str=None
        evo_type:str=None
        evo_condition:str=None
        gender:dict=None
        evolution:str=None
        forms:list=None
        image:str=None
        shiny_image:str=None

        def __str__(self):
            return (
                f"Pokemon #{self.number}: {self.name}\n"
                f"Description: {self.description}\n\n"

                f"--- Physical ---\n"
                f"Height: {self.height}\n"
                f"Weight: {self.weight}\n"
                f"Color: {self.color}\n\n"

                f"--- Types & Abilities ---\n"
                f"Types: {self.types}\n"
                f"Abilities: {self.abilites}\n\n"

                f"--- Stats ---\n"
                f"HP: {self.hp}\n"
                f"Attack: {self.attack}\n"
                f"Defense: {self.defense}\n"
                f"Sp. Attack: {self.sp_attack}\n"
                f"Sp. Defense: {self.sp_defense}\n"
                f"Speed: {self.speed}\n\n"

                f"--- Images ---\n"
                f"Image: {self.image}\n"
                f"Shiny Image: {self.shiny_image}\n"
                f"Is Shiny: {self.is_shiny}\n\n"

                f"--- Breeding ---\n"
                f"Gender: {self.gender}\n"
                f"Egg Groups: {self.egg_group}\n\n"

                f"--- Evolution ---\n"
                f"Pre-evolutions: {self.pre_evolutions}\n"
                f"Evolution: {self.evolution}\n"
                f"Evolution Type: {self.evo_type}\n"
                f"Evolution Condition: {self.evo_condition}\n\n"

                f"--- Competitive ---\n"
                f"Tier: {self.tier}\n"
                f"Forms: {self.forms}"
            )
    
    async def get_pokemon(self, pokemon:str, shiny:bool=False):
        # Pokeapi request for images(home) and description
        # Rest can be pulled from the json
        # TODO: Allow search with numbers .
        # TODO: Add forms to a dropdown, would be pretty cool.
        is_numeric = False
        if pokemon.isdigit():
            is_numeric = True
            pokemon = int(pokemon)
        else:
            pokemon = pokemon.lower()
        with open("Bot_Databases/pokedex.json", 'r', encoding="utf-8") as file:
            data:dict = json.load(file)

            found = False

            if is_numeric:
                for key, entry in data.items():
                    if entry.get("num") == pokemon:
                        data = data.get(entry["name"].lower())
                        found = True
                        break
                if not found:
                    data = None
            else:
                data = data.get(pokemon)

            if data == None:
                return None

            # Image grabbing
            api = "https://archives.bulbagarden.net/w/api.php"
            
            titles = ""
            titles = f"{data['num']:04d}"
            
            #check for forms
            form = data.get('forme', None)

            home = "HOME"

            if form:
                if form == "Mega":
                    titles = titles + "M"
                elif form == "Mega-Z":
                    # Game freak please put Z forms in home I beg you
                    titles = f"{data['num']:04d}{data["baseSpecies"]}-Mega_Z"
                    home = ""
                elif form == "Gmax":
                    titles = titles + "Gi"

            if shiny and form != "Mega-Z":
                titles = f"{titles}_s"

            params = {
                "action": "query",
                "titles": f"File:{home}{titles}.png",
                "prop": "imageinfo",
                "iiprop": "url",
                "format": "json"
            }

            img_response = requests.get(api, params=params).json()
            image_data = None

            if img_response is not None:
                pages = img_response["query"]["pages"]
                image_data = list(pages.values())[0]["imageinfo"][0]["url"]

            description_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon}"

            flavor_text = ""
            response = requests.get(description_url)
            if response.status_code == 404:
                flavor_text = "Description not available."
            else:
                description_data = response.json()
                # Grab the flavor text from this shitty api holy shit who made this
                for description in description_data["flavor_text_entries"]:
                    if description["language"]["name"] == "en":
                        flavor_text = description["flavor_text"]
                        break

            to_return = self.Pokemon_data(name=data["name"],
                                          number=data["num"],
                                          description=flavor_text,
                                          height=data["heightm"],
                                          color=data["color"],
                                          weight=data["weightkg"],
                                          abilites=data["abilities"],
                                          types=data["types"],
                                          hp=data["baseStats"]["hp"],
                                          attack=data["baseStats"]["atk"],
                                          defense=data["baseStats"]["def"],
                                          sp_attack=data["baseStats"]["spa"],
                                          sp_defense=data["baseStats"]["spd"],
                                          speed=data["baseStats"]["spe"],
                                          image=image_data,
                                          shiny_image=image_data,
                                          is_shiny=shiny,
                                          gender=data.get("genderRatio"),
                                          evolution=None,
                                          pre_evolutions=data.get("prevo"),
                                          evo_type=data.get("evoType"),
                                          evo_condition=data.get("evoCondition"),
                                          egg_group=data["eggGroups"],
                                          tier=data["tier"],
                                          forms=data.get("otherFormes"))
        return to_return



    @app_commands.command(name="pokemon", description="Shows information about a pokemon.")
    @app_commands.describe(pokemon="Name of the pokemon to lookup")
    async def pokemon_info(self, interaction:discord.Interaction, pokemon:str):
        await interaction.response.defer()
        shiny = random.randint(1, 1024)

        if shiny == 621:
            shiny = True
        else:
            shiny = False

        pokemon_data = await self.get_pokemon(pokemon, shiny)

        if pokemon_data == None:
            await interaction.followup.send("Pokemon not found.")
            return
        
        if shiny:
            embed = discord.Embed(
                title=f"{pokemon_data.name} (Nº{pokemon_data.number})✨",
                description=f"*{pokemon_data.description}*"
            )
        else:
            embed = discord.Embed(
                title=f"{pokemon_data.name} (Nº{pokemon_data.number})",
                description=f"*{pokemon_data.description}*"
            )

        colors = {
            "Black":0x000000,
            "Blue":0x56a0ea,
            "Brown":0xA52A2A,
            "Gray":0x808080,
            "Green":0x008000,
            "Pink":0xFFC0CB,
            "Purple":0x800080,
            "Red":0xFF0000,
            "White":0xFFFFFF,
            "Yellow":0xFFFF00
        }

        embed.color = colors[pokemon_data.color]

        if pokemon_data.image == None:
            embed.set_thumbnail(url="https://static.wikia.nocookie.net/pokemon/images/7/7f/Substitute_USUM_artwork.png/revision/latest?cb=20250412130621")
        else:
            embed.set_thumbnail(url=pokemon_data.image)
        
        types_string = ""

        for type in pokemon_data.types:
            if len(types_string) == 0:
                types_string += type
            else:
                types_string += f", {type}"
        

        embed.add_field(name="Types", value=types_string)

        if pokemon_data.gender:
            embed.add_field(name="Gender Percentages", value=f"M: {pokemon_data.gender["M"]*100}%\nF: {pokemon_data.gender["F"]*100}%")
        else:
            embed.add_field(name="Gender Percentages", value="Unknown")
        
        ability_string = ""

        for key, ability in pokemon_data.abilites.items():
            if len(ability_string) == 0:
                ability_string += ability
            else:
                if key == "H":
                    ability_string += f"*, {ability}*"
                else:
                    ability_string += f", {ability}"

        embed.add_field(name="Abilities", value=ability_string)

        total = pokemon_data.hp + pokemon_data.attack + pokemon_data.defense + pokemon_data.sp_attack + pokemon_data.sp_defense + pokemon_data.speed
        
        stats_string = f"**Hp:**{pokemon_data.hp},**Atk:**{pokemon_data.attack},**Def:**{pokemon_data.defense},**Spa:**{pokemon_data.sp_attack},**Spd:**{pokemon_data.sp_defense},**Spe:**{pokemon_data.speed},**Total:**{total}"

        embed.add_field(name="Stats", value=stats_string, inline=False)

        if pokemon_data.pre_evolutions:
            embed.add_field(name="Pre-Evolution", value=pokemon_data.pre_evolutions, inline=False)
            embed.add_field(name="Evolution Conditions", value=f"{pokemon_data.evo_type} ({pokemon_data.evo_condition})", inline=True)
        else:
            embed.add_field(name="Pre-Evolution", value="None", inline=False)

        embed.add_field(name="Height", value=f"{pokemon_data.height}m", inline=False)
        embed.add_field(name="Weight", value=f"{pokemon_data.weight}kg", inline=False)
        embed.add_field(name="Tier", value=pokemon_data.tier, inline=True)

        egg_string = ""

        for egg in pokemon_data.egg_group:
            if len(egg_string) == 0:
                egg_string += egg
            else:
                egg_string += f", {egg}"

        embed.add_field(name="Egg Group", value=egg_string, inline=False)

        embed.set_footer(text="Data is from Showdown, Image is from Bulbagarden, description is from PokeAPI. Description is from the generation where the pokemon was introduced")

        await interaction.followup.send(embed=embed)
        



async def setup(bot):
    await bot.add_cog(Pokemon(bot))