"""Module for searching youtube with search terms, youtube links and spotify links."""

from dotenv import load_dotenv
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib
import youtube_dl

# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def searchYoutube(searchTerms: str):
    """Searches on Youtube and returns the link of the top result."""
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + searchTerms.replace(" ", "+"))
    search_html = html.read().decode()
    resultTemplate = r"watch\?v=.{11}"
    vid_id = re.search(resultTemplate, search_html).group(0)
    link = r"https://youtube.com/" + vid_id
    return link

def getSpotifySingle(link):
    """Finds the name of a song from a spotify link and then searches for it on youtube."""
    auth = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth)

    track = sp.track(link)
    searchTerms = track["name"] + " - " + track["album"]["artists"][0]["name"]
    return searchYoutube(searchTerms)

def getSpotifyPlaylist(link):
    """Returns a list of youtube links corresponding to songs in a spotify playlist."""
    auth = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth)

    songs = []
    playlist = sp.playlist_tracks(link)
    for item in playlist["items"]:
        track = item["track"]
        searchTerms = track["name"] + " - " + track["album"]["artists"][0]["name"]
        try:
            songs.append(searchYoutube(searchTerms))
        except:
            pass
    return songs

def isYoutubeVideo(query):
    return bool(re.search("^https://www.youtube.com/watch?v=.{11}", query)) or bool(re.search("^https://youtu.be/.{11}", query))

def isSpotifySong(query):
    return bool(re.search("^https://open.spotify.com/track/.{42}", query))

def isSpotifyPlaylist(query):
    return bool(re.search("^https://open.spotify.com/playlist/.{42}", query))