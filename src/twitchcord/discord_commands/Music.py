import discord
from discord.ext import commands
from discord.ext import tasks
import re
import youtube_dl

from ..Music import search

FFMPEG_DIR = r"C:\Users\Alex\Downloads\ffmpeg-2021-09-20-git-59719a905c-essentials_build\bin\ffmpeg.exe"
FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
        }

class Song():
    """Object that represents a song, with a title and url."""

    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url


class Music(commands.Cog):
    """Used to make JezzaBot play music from youtube. RIP Groovy."""

    def __init__(self, client: commands.Bot):
        self.client = client
        self.queues = {}
        self.active_channel = None

        ytdl_format_options = {
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
        'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
        }

        self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

        self.update_queues.start()

    async def display_now_playing(self, ctx: commands.Context, song: Song):
        """Send a message showing the currently playing song."""
        await ctx.send(f"Now playing: **{song.title}**.")

    async def display_added_to_queue(self, ctx: commands.Context, song: Song):
        """Send a message showing that a song has been added to the queue."""
        await ctx.send(f"**{song.title}** added to queue.")


    def add_to_queue(self, song: Song, guild: discord.Guild):
        """Add a song to the queue of a specific server."""
        if not guild.id in self.queues:
            self.queues[guild.id] = []
        self.queues[guild.id].append(song)

    def play_raw(self, voice: discord.VoiceClient, song: Song):
        """Just plays a song without any checking. Doesn't connect to channels or check if a song is already playing, so should be only used within other functions and not as is."""
        audio = discord.FFmpegPCMAudio(executable=FFMPEG_DIR, source=song.url, **FFMPEG_OPTIONS)
        voice.play(audio)

    def play_next(self, voice: discord.VoiceClient, guild: discord.Guild):
        """Play the next song in the queue."""
        self.queues[guild.id].pop(0)
        nextSong = self.queues[guild.id][0]
        self.play_raw(voice, nextSong)

    @tasks.loop(seconds=5)
    async def update_queues(self):
        """Checks if any voice clients aren't playing music, and if so plays the next song in the queue if there is one."""
        for voice in self.client.voice_clients:
            guild = voice.guild
            if not guild.id in self.queues:
                self.queues[guild.id] = []
            if (not voice.is_playing()) and len(self.queues[guild.id]) == 1:
                self.queues[guild.id].pop(0)
            if (not voice.is_playing()) and len(self.queues[guild.id]) > 1:
                self.play_next(voice, guild)

    @update_queues.before_loop
    async def before_update_queues(self):
        await self.client.wait_until_ready()
                



    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *, userInput):
        """Plays a given song.
        
        Accepts Youtube links, Spotify links, and search terms for Youtube."""

        voice: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        # If no song is given, command is either used to resume if paused or sends a message otherwise

        if not userInput:
            if voice:
                if voice.is_paused():
                    voice.resume()
                    return
            await ctx.send("No song found to play!")
            return

        # Search youtube for song

        if search.isYoutubeVideo(userInput):
            link = userInput

        elif search.isSpotifySong(userInput):
            link = search.getSpotifySingle(userInput)

        elif search.isSpotifyPlaylist(userInput):
            for link in search.getSpotifyPlaylist(userInput):
                info = self.ytdl.extract_info(link, download=False)
                song = Song(info['title'], info['url'])
                self.add_to_queue(song, ctx.guild)
            link = self.queues[ctx.guild.id][0].url

        else:
            link = search.searchYoutube(userInput)

        # Move to the right channel or join if not already connected

        voiceChannel: discord.VoiceChannel = ctx.author.voice.channel
        if voice and voice.is_connected():
            await voice.move_to(voiceChannel)
        else:
            voice = await voiceChannel.connect()

        # Get youtube video

        info = self.ytdl.extract_info(link, download=False)
        song = Song(info['title'], info['url'])

        # Check if bot is already playing a song

        if voice.is_playing():
            # Add song to queue
            self.add_to_queue(song, ctx.guild)
            await self.display_added_to_queue(ctx, song)
        else:
            # Play song
            self.add_to_queue(song, ctx.guild)
            self.play_raw(voice, song)
            await self.display_now_playing(ctx, song)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing song."""
        voice: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.pause()

    @commands.command()
    async def resume(self, ctx: commands.Context):
        """Resume the currently playing song."""
        voice: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_paused():
            voice.resume()

    @commands.command()
    async def stop(self, ctx: commands.Context):
        """Stop the currently playing song."""
        voice: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.stop()

    @commands.command(aliases=["next", "n", "s"])
    async def skip(self, ctx: commands.Context):
        """Skip to the next song in the queue if there is one."""
        voice: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        guild: discord.Guild = ctx.guild

        voice.stop()

        if len(self.queues[guild.id]) > 1:
            self.play_next(voice, guild)

    @commands.command(aliases=["q"])
    async def queue(self, ctx: commands.Context):
        """Display the song queue."""

        guildID = ctx.guild.id

        if not ctx.guild.id in self.queues:
            self.queues[guildID] = []

        if len(self.queues[guildID]) == 0:
            await ctx.send("The queue is empty!")
        else:
            queue = "**Current Song Queue:**"
            i = 1
            for song in self.queues[guildID]:
                queue += f"\n{i:2>}) {song.title}"
                if i == 1:
                    queue += "  **<- Now Playing**"
                i += 1

            await ctx.send(queue)


        






def setup(client: commands.Bot):
    client.add_cog(Music(client))