import asyncio
import os
from dotenv import load_dotenv
from twitchcord.DualClient import dualClient
import discord
from discord import Intents
from discord.ext import commands as dscCommands
import twitchio
from twitchio.ext import commands as twtCommands

import random

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
for filename in os.listdir("twitchcord/discord_commands"):
    if filename[-3:] == ".py" and filename != "__init__.py" and filename != "Testing.py":
        try:
            if DEBUG:
                print(f"Attempting to load module \"{filename}\"...")
            discordClient.load_extension(f"twitchcord.discord_commands.{filename[:-3]}")
            if DEBUG:
                print(f"Successfully loaded module \"{filename}\".")
        except Exception as e:
            print(f"Couldn't load module \"{filename}\": {e}")

if DEBUG:
    discordClient.load_extension("twitchcord.discord_commands.Testing")

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

# Bruh----------------------------------------

agents =  [
    "Brimstone",
    "Viper",
    "Omen",
    "Killjoy",
    "Cypher",
    "Sova",
    "Sage",
    "Phoenix",
    "Jett",
    "Reyna",
    "Raze",
    "Breach",
    "Skye",
    "Yoru",
    "Astra",
    "KAY/O",
    "Chamber",
    "Neon",
    "Fade",
    "Harbor"
]

pistols = [
    "Knife",
    "Classic",
    "Shorty",
    "Frenzy",
    "Ghost",
    "Sheriff"
]

guns = [
    "Knife",
    "Classic",
    "Shorty",
    "Frenzy",
    "Ghost",
    "Sheriff",
    "Stinger",
    "Spectre",
    "Bucky",
    "Judge",
    "Bulldog",
    "Guardian",
    "Phantom",
    "Vandal",
    "Marshal",
    "Operator",
    "Ares",
    "Odin"
]

@twitchClient.command()
async def randomChar(ctx: twtCommands.Context, number: int = 1):
    if number > 5:
        await ctx.send("Maximum number is 5!")
        return
    if number == 1:
        index = random.randrange(0, len(agents) - 1)
        await ctx.send(f"@{ctx.author.name} {agents[index]}")
        return
    message = ""
    used = []
    for i in range(number):
        index = random.randrange(0, len(agents) - 1)
        while index in used:
            index = random.randrange(0, len(agents) - 1)
        used.append(index)
        message += f"{i + 1}) {agents[index]}{' | ' if i < number - 1 else ''}"
    await ctx.send(message)

@twitchClient.command()
async def randomPistol(ctx: twtCommands.Context, number: int = 1):
    if number > 5:
        await ctx.send("Maximum number is 5!")
    if number == 1:
        index = random.randrange(0, len(pistols) - 1)
        await ctx.send(f"@{ctx.author.name} {pistols[index]}")
        return
    message = ""
    for i in range(number):
        index = random.randrange(0, len(pistols) - 1)
        message += f"{i + 1}) {pistols[index]}{' | ' if i < number - 1 else ''}"
    await ctx.send(message)

@twitchClient.command()
async def randomGun(ctx: twtCommands.Context, number: int = 1):
    if number > 5:
        await ctx.send("Maximum number is 5!")
    if number == 1:
        index = random.randrange(0, len(guns) - 1)
        await ctx.send(f"@{ctx.author.name} {guns[index]}")
        return
    message = ""
    for i in range(number):
        index = random.randrange(0, len(guns) - 1)
        message += f"{i + 1}) {guns[index]}{' | ' if i < number - 1 else ''}"
    await ctx.send(message)

# Bruh----------------------------------------

print("Starting bots...")
JezzaBot.run()