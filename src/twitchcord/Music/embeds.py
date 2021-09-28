from math import ceil
from typing import List

from discord import Embed
from .song import Song

def nowPlaying(song: Song) -> Embed:
    embed = Embed(
        title = "Now playing",
        description = f"[{song.title}]({song.yt_link}) [{song.added_by.mention}]",
        color=0xf0e7a1
    )
    return embed

def queuedSong(song: Song) -> Embed:
    embed = Embed(
        description = f"Queued [{song.title}]({song.yt_link}) [{song.added_by.mention}]",
        color=0xf0e7a1
    )
    return embed

def queuedSongs(numberSongs: int) -> Embed:
    embed = Embed(
        description = f"Queued **{numberSongs}** tracks",
        color=0xf0e7a1
    )
    return embed
    
def currentlyPlaying(song: Song) -> Embed:
    embed = Embed(
        description = f"[{song.title}]({song.yt_link}) [{song.added_by.mention}]",
        color=0xf0e7a1
    )
    return embed

def notPlaying() -> Embed:
    embed = Embed(
        description = "Not currently playing a song!",
        color=0xf0e7a1
    )
    return embed

def queue(queue: List[Song], fromSongNo: int = 0) -> str:
    if len(queue) == 0:
        msg = "```The queue is empty!```"
    else:
        msg = "```"
        minNo = min(fromSongNo + 10, len(queue) - fromSongNo)
        for i in range(fromSongNo, minNo):
            song = queue[i]
            msg += f"\n{i + 1:2>}) {song.title} - {song.duration.toString()}"
        msg += "```"
    return msg