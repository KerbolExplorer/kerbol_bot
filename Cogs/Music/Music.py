import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import re
import math

YOUTUBE_URL_PATTERN = re.compile(
    r"^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(watch\?v=|embed\/|shorts\/|live\/|.+\?v=)?([^&\n]+)"
    )

# Setup Youtube DL library
ytdl_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

#setup FFmpeg
ffmpeg_options = {
    #'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', <- testing some stuff to avoid the bot from dying mid song
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -reconnect_at_eof 1',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.uploader = data.get('uploader', 'Unkown Artist')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data: # <-- this bad boy handles if you gave it a playlist TODO: Make sure the user wants to give solgaleo the entire playlist
            return [cls(discord.FFmpegPCMAudio(entry['url'], **ffmpeg_options), data=entry) for entry in data['entries']]
        else:
            return [cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)]

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_voice_channel = None
        self.queue = asyncio.Queue()
        self.is_playing = False
        self.current_song = None
        self.skip_votes = set() 

        is_skipping : bool = False


    async def play_next(self, interaction):
        if self.queue.empty():
            self.is_playing = False
            self.current_song = None
        
            vc = interaction.guild.voice_client
            if vc and vc.is_connected():
                await vc.disconnect()
                await interaction.followup.send("Finished playing the songs, leaving the vc")
            return
        
        
        self.is_playing = True
        vc = interaction.guild.voice_client

        self.current_song = await self.queue.get()
        vc.play(self.current_song, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop))

        await interaction.followup.send(f"Now playing: {self.current_song.title}")

            

    @app_commands.command(name="play", description="Plays the video sent in the url or adds it to the queue")
    async def play(self, interaction: discord.Interaction, url: str):

        if not YOUTUBE_URL_PATTERN.match(url):
            await interaction.response.send_message("The link is not valid. It is either not a youtube link or you accidentally copied the thumbnail", ephemeral=True)
            return

        await interaction.response.defer()      #Makes discord wait for the bot

        if not interaction.guild.voice_client:
           self.current_voice_channel = await interaction.user.voice.channel.connect()

        songs = await YTDLSource.from_url(url, stream=True)

        for song in songs:
            await self.queue.put(song)

        await interaction.followup.send(f"Added {len(songs)} song(s) to the queue!")
        
        if not self.is_playing:
            await self.play_next(interaction)

    @app_commands.command(name="skip", description="Starts a vote to skip the current song")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client

        if not vc or not vc.is_playing():
            await interaction.response.send_message("There's no song playing", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        if not voice_channel:
            await interaction.response.send_message("You must be in a voice channel to vote!", ephemeral=True)
            return

        total_members = len([m for m in voice_channel.members if not m.bot])
        required_votes = math.ceil(total_members / 2)

        if interaction.user.id in self.skip_votes:
            await interaction.response.send_message("You have already voted to skip!", ephemeral=True)
            return

        self.skip_votes.add(interaction.user.id)
        current_votes = len(self.skip_votes)

        if current_votes >= required_votes:
            vc.stop()
            self.skip_votes.clear()
            await interaction.response.send_message("Vote successful! Skipped the current song.")
            return

        await interaction.response.send_message(f"Vote added! {current_votes}/{required_votes} votes needed.")
        await asyncio.sleep(60)

        if len(self.skip_votes) >= required_votes:
            vc.stop()
            self.skip_votes.clear()
            await interaction.followup.send("Vote successful! Skipped the current song.")
        else:
            self.skip_votes.clear()
            await interaction.followup.send("Vote failed. Not enough votes to skip the song.")

    @app_commands.command(name="force_skip", description="[Requires channel management permision]")
    async def force_skip(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_channels:
            if self.is_skipping:
                await interaction.response.send_message("I'm already skipping a song. Wait a sec", ephemeral=True)
                return
            self.is_skipping = True
            vc = interaction.guild.voice_client
            if vc and vc.is_playing():
                vc.stop()
                await interaction.response.send_message("Skipped the current song")
                self.is_skipping = False
                self.counting_skip = False
            else:
                await interaction.response.send_message("There's no song playing", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have the required permisions to use this command", ephemeral=True)


    @app_commands.command(name="queue", description="Shows the curren song queue")
    async def queue_list(self, interaction: discord.Interaction):
        if self.queue.empty():
            await interaction.response.send_message("The queue is empty")
        else:
            queue_list = list(self.queue._queue)  # Get queue items
            description_text = "\n".join(song.title for song in queue_list)
            embed = discord.Embed(description=description_text, color=0xf1c40f, title="Music Queue")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="now_playing", description="Shows what song is currently playing")
    async def now_playing(self, interaction: discord.Interaction):
        if self.current_song:
            await interaction.response.send_message(f"Now playing - **{self.current_song.title}** by {self.current_song.uploader}")
        else:
            await interaction.response.send_message("No song is currently playing.", ephemeral=True)

    @app_commands.command(name="stop", description="Stops all songs and leaves the vc")
    async def stop(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_channels:
            vc = interaction.guild.voice_client
            if vc and vc.is_connected():
                await vc.disconnect()
                await interaction.response.send_message("Left the voice channel")
            else:
                await interaction.response.send_message("I'm not in any voice channels", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have the required persmisions to use this command", ephemeral=True)
        


async def setup(bot):
    await bot.add_cog(Music(bot))