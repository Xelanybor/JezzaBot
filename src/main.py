import asyncio
import os
from dotenv import load_dotenv
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
intents.message_content = True

# Create discord bot
    
class Bot(dscCommands.Bot):
    """Custom bot class that extends `discord.ext.commands.Bot`.
    """
    
    def __init__(self):
        super().__init__(
            command_prefix=DISCORD_PREFIX,
            intents=intents,
            case_insensitive=True,
            status=discord.Status.online, 
            activity=discord.Game(name=f"{DISCORD_PREFIX}help for help!")
        )
    
discordBot = Bot()

# Load cogs
async def startDiscordBot():

    for filename in os.listdir("twitchcord/discord_commands"):
        if filename[-3:] == ".py" and filename != "__init__.py" and filename != "Testing.py":
            try:
                if DEBUG:
                    print(f"Attempting to load module \"{filename}\"...")
                await discordBot.load_extension(f"twitchcord.discord_commands.{filename[:-3]}")
                if DEBUG:
                    print(f"Successfully loaded module \"{filename}\".")
            except Exception as e:
                print(f"Couldn't load module \"{filename}\": {e}")

    if DEBUG:
        print(f"Attempting to load module \"Testing.py\"...")
        await discordBot.load_extension("twitchcord.discord_commands.Testing")
        print(f"Successfully loaded module \"Testing.py\".")
    
    # Discord Bot setup
        
    @discordBot.event
    async def on_ready():
        print(f'Logged into Discord as {discordBot.user}.')        
    
    async with discordBot:
        await discordBot.start(DISCORD_TOKEN)
        

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

async def startTwitchBot():
    @twitchClient.event()
    async def event_ready():
        print(f'Logged into Twitch as {TWITCH_NICK[0]}.')

    @twitchClient.command()
    async def test(ctx):
        await ctx.send("yep it works")
        
    await twitchClient.connect()
    
    
if __name__ == "__main__":
    print("Starting bots...") 
       
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(startDiscordBot())
        loop.create_task(startTwitchBot())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting down bots...")
        loop.run_until_complete(twitchClient.close())
        loop.close()