from discord.ext import commands
from discord.ext.commands.errors import ExtensionAlreadyLoaded, ExtensionFailed, ExtensionNotFound, ExtensionNotLoaded, NoEntryPointError

class Cogs(commands.Cog):
    "Loads, unloads, and reloads command cogs."

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def load(self, ctx: commands.Context, cog: str):
        "Load a given cog."
        try:
            self.client.load_extension(f"twitchcord.discord_commands.{cog}")
            await ctx.send(f"Successfully loaded cog `{cog}`.")
        except ExtensionNotFound as e:
            await ctx.send(f"Cog `{e.name}` was unable to be found!")
        except ExtensionAlreadyLoaded as e:
            await ctx.send(f"Cog `{e.name}` is already loaded!")
        except NoEntryPointError or ExtensionFailed as e:
            await ctx.send(f"Unable to load cog: {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx: commands.Context, cog: str):
        "Unload a given cog."
        try:
            self.client.unload_extension(f"twitchcord.discord_commands.{cog}")
        except ExtensionNotFound as e:
            await ctx.send(f"Cog `{e.name}` was unable to be found!")
        except ExtensionNotLoaded as e:
            await ctx.send(f"Cog `{e.name}` is already unloaded!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx: commands.Context, cog: str):
        "Reload a given cog."
        try:
            self.client.reload_extension(f"twitchcord.discord_commands.{cog}")
        except ExtensionNotFound as e:
            await ctx.send(f"Cog `{e.name}` was unable to be found!")

def setup(client: commands.Bot):
    client.add_cog(Cogs(client))