import asyncio
import os
from dotenv import load_dotenv
from twitchcord.DualClient import dualClient
import discord
from discord import Intents
from discord.ext import commands as dscCommands
import twitchio
from twitchio.ext import commands as twtCommands

# Debug initialization
# ---------------------------------------------------------------------------------
load_dotenv()
try:
    if os.getenv("DEBUG").lower() == "true":
        DEBUG = True
    else:
        DEBUG = False
except:
    DEBUG = False

# Discord bot initialization
# ---------------------------------------------------------------------------------

# Load variables from the .env
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_PREFIX = os.getenv("PREFIX")

# Don't need this just yet but will make adding special intents later easier
intents = Intents.default()
intents.members = False

# Create discord bot
discordClient = dscCommands.Bot(
    command_prefix=DISCORD_PREFIX,
    intents=intents,
    case_insensitive=True
    )

# Load cogs
for filename in os.listdir("src/twitchcord/discord_commands"):
    if filename[-3:] == ".py" and filename != "__init__.py":
        try:
            if DEBUG:
                print(f"Attempting to load module \"{filename}\"...")
            discordClient.load_extension(f"twitchcord.discord_commands.{filename[:-3]}")
            if DEBUG:
                print(f"Successfully loaded module \"{filename}\".")
        except Exception as e:
            print(f"Couldn't load module \"{filename}\": {e}")

# Twitch bot initialization
# ---------------------------------------------------------------------------------

# Load variables from the .env
TWITCH_TOKEN = os.getenv('TWITCH_TOKEN'),
TWITCH_CLIENT_ID=os.getenv('TWITCH_CLIENT_ID'),
TWITCH_NICK=os.getenv('TWITCH_NICK'),
TWITCH_PREFIX=os.getenv('PREFIX'),
TWITCH_INITIAL_CHANNELS=os.getenv('TWITCH_CHANNELS').split(" ")

# Create twitch bot
twitchClient = twtCommands.Bot(
    token = TWITCH_TOKEN[0],
    client_id = TWITCH_CLIENT_ID,
    nick = TWITCH_NICK,
    prefix = TWITCH_PREFIX,
    initial_channels = TWITCH_INITIAL_CHANNELS
)

# Bot startup
# ---------------------------------------------------------------------------------

JezzaBot = dualClient(discordClient, twitchClient, DISCORD_TOKEN)

@discordClient.event
async def on_ready():
    print(f'Logged into Discord as {discordClient.user}.')
    await discordClient.change_presence(
        status=discord.Status.online, 
        activity=discord.Game(name="-help for help!")
        )

@twitchClient.event()
async def event_ready():
    print(f'Logged into Twitch as {TWITCH_NICK[0]}.')

@twitchClient.command()
async def test(ctx):
    await ctx.send("yep it works")

print("Starting bots...")
JezzaBot.run()