import discord

class duration():
    """Object to store the duration of a song."""

    def __init__(self, hours: int, minutes: int, seconds: int):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def toString(self):
        if self.hours:
            return f"{self.hours}:{self.minutes:02d}:{self.seconds:02d}"
        else:
            return f"{self.minutes:02d}:{self.seconds:02d}"

class Song():
    """Object that represents a song, with a title and url."""

    def __init__(self, title: str, url: str, added_by: discord.User, yt_link: str, durationSeconds: int):
        self.title = title
        self.url = url
        self.added_by = added_by
        self.yt_link = yt_link

        seconds = durationSeconds
        hours = seconds // 3600
        seconds = seconds % 3600
        minutes = seconds // 60
        seconds = seconds % 60
        self.duration = duration(hours, minutes, seconds)

    def getDuration(self) -> str:
        return self.duration.toString