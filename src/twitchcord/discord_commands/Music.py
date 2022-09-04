from typing import Union
import discord
from discord import guild, app_commands
from discord.ext import commands
from discord.ext import tasks
import youtube_dl

from ..Music import search
from ..Music import embeds
from ..Music.song import Song

FFMPEG_DIR = r"C:\Users\Alex\Downloads\ffmpeg-2021-09-20-git-59719a905c-essentials_build\bin\ffmpeg.exe"
FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
        }

class Music(commands.Cog):
    """Used to make JezzaBot play music from youtube. RIP Groovy."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues = {}
        self.active_channel = {}
        self.last_now_playing = {}
        
        self.queuing_songs = False

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

    @commands.before_invoke
    async def setActiveChannel(self, ctx):
        """Update the guild's currently active channel to send messages in."""
        self.active_channel[ctx.guild.id] = ctx.channel

    async def display_now_playing(self, ctx, song: Song):
        """Send a message when a song starts playing."""
        if ctx.guild.id in self.last_now_playing:
            await self.last_now_playing[ctx.guild.id].delete()
        self.last_now_playing[ctx.guild.id] = await ctx.send(embed=embeds.nowPlaying(song))

    async def display_currently_playing(self, ctx, song: Song = None):
        """Send a message about the song currently playing."""

        if not song:
            await ctx.send(embed=embeds.notPlaying())
            return
        try:
            voice: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        except:
            await ctx.send(embed=embeds.notPlaying())
            return
        if voice.is_playing():
            await ctx.send(embed=embeds.currentlyPlaying(song))
        else:
            await ctx.send(embed=embeds.notPlaying())

    async def display_added_to_queue(self, ctx: commands.Context, song: Song):
        """Send a message showing that a song has been added to the queue."""
        await ctx.send(embed=embeds.queuedSong(song))


    def add_to_queue(self, song: Song, guild: discord.Guild):
        """Add a song to the queue of a specific server."""
        if not guild.id in self.queues:
            self.queues[guild.id] = []
        self.queues[guild.id].append(song)

    def play_raw(self, voice: discord.VoiceClient, song: Song):
        """Just plays a song without any checking. Doesn't connect to channels or check if a song is already playing, so should be only used within other functions and not as is."""
        audio = discord.FFmpegPCMAudio(executable=FFMPEG_DIR, source=song.url, **FFMPEG_OPTIONS)
        voice.play(audio)

    async def play_next(self, voice: discord.VoiceClient, guild: discord.Guild):
        """Play the next song in the queue."""
        self.queues[guild.id].pop(0)
        nextSong = self.queues[guild.id][0]
        self.play_raw(voice, nextSong)
        await self.display_now_playing(self.active_channel[guild.id], nextSong)

    @tasks.loop(seconds=5)
    async def update_queues(self):
        """Checks if any voice clients aren't playing music, and if so plays the next song in the queue if there is one."""
        for voice in self.bot.voice_clients:
            guild = voice.guild
            if not guild.id in self.queues:
                self.queues[guild.id] = []
            if (not voice.is_playing()) and len(self.queues[guild.id]) == 1:
                self.queues[guild.id].pop(0)
            if (not voice.is_playing()) and len(self.queues[guild.id]) > 1:
                if not self.queuing_songs:
                    await self.play_next(voice, guild)

    @update_queues.before_loop
    async def before_update_queues(self):
        await self.bot.wait_until_ready()
                



    @app_commands.command()
    async def play(self, ctx: commands.Context, *, searchTerm: str):
        """Plays a given song.
        
        Accepts Youtube links, Spotify links, and search terms for Youtube."""
        
        userInput = searchTerm

        self.queuing_songs = True

        # Set active channel

        self.active_channel[ctx.guild.id] = ctx.channel

        voice: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # If no song is given, command is either used to resume if paused or sends a message otherwise

        playlist = False

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
            playlist = search.getSpotifyPlaylist(userInput)
            for link in playlist:
                info = self.ytdl.extract_info(link, download=False)
                song = Song(info['title'], info['url'], ctx.author, link, info['duration'])
                self.add_to_queue(song, ctx.guild)
            link = self.queues[ctx.guild.id][0].yt_link
            await ctx.send(embed=embeds.queuedSongs(len(playlist)))
            playlist = True

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
        song = Song(info['title'], info['url'], ctx.author, link, info['duration'])

        # Check if bot is already playing a song

        # Add song to queue
        if not playlist:
            self.add_to_queue(song, ctx.guild)

        if voice.is_playing():
            # Display the song added
            await self.display_added_to_queue(ctx, song)
        else:
            # Play song
            self.play_raw(voice, song)
            await self.display_now_playing(ctx, song)

        self.queuing_songs = False

    @app_commands.command()
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing song."""
        voice: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.pause()

    @app_commands.command()
    async def resume(self, ctx: commands.Context):
        """Resume the currently playing song."""
        voice: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice.is_paused():
            voice.resume()

    @app_commands.command()
    async def stop(self, ctx: commands.Context):
        """Stop the currently playing song."""
        voice: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.stop()

    @app_commands.command()
    async def skip(self, ctx: commands.Context):
        """Skip to the next song in the queue if there is one."""
        voice: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        guild: discord.Guild = ctx.guild

        voice.stop()

        if len(self.queues[guild.id]) > 1:
            await self.play_next(voice, guild)

    @app_commands.command()
    async def queue(self, ctx: commands.Context):
        """Display the song queue."""

        guildID = ctx.guild.id

        if not ctx.guild.id in self.queues:
            self.queues[guildID] = []

        if len(self.queues[guildID]) == 0:
            await ctx.send("The queue is empty!")
        else:
            message = embeds.queue(self.queues[guildID], 0)
            await ctx.send(message)

    @app_commands.command()
    async def nowplaying(self, ctx: commands.context):
        """Displays the song that is currently playing."""

        if not ctx.guild.id in self.queues:
            self.queues[ctx.guild.id] = []
            await self.display_currently_playing(ctx)
        else:
            await self.display_currently_playing(ctx, self.queues[ctx.guild.id][0])


        






async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))