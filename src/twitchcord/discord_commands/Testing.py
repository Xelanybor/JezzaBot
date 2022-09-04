import discord
from discord import app_commands
from discord.ext import commands
from typing import *

from ..sql.MainConnection import mainConnection
from ..Music.song import Song
from ..Music import embeds

class Testing(commands.Cog):
    """Testing commands cause idk what I'm doing lol."""

    def __init__(self, bot: commands.Bot):
        super().__init__
        self.bot = bot

    @commands.hybrid_command()
    async def test(self, ctx):
        await ctx.reply("yep it works")
        
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=259293507955589121))
    async def bruh(self, ctx: discord.Interaction):
        """Bruh moment
        """
        await ctx.response.send_message("bruh")
        
    @commands.command(name="localsync")
    async def localsync(self, ctx: commands.Context):
        """Sync bot commands locally to the guild the command is called in.

        Args:
            ctx (commands.Context): _description_
        """
        
        print(f"Attempting to sync commands in guild {ctx.guild.name}...")
        await ctx.reply(f"Attempting to sync commands in guild {ctx.guild.name}...")
        
        try:
            self.bot.tree.copy_global_to(guild=discord.Object(id=ctx.guild.id))
            await self.bot.tree.sync(guild=discord.Object(id=ctx.guild.id))
        except Exception as e:
            print(e.with_traceback())
        print("Commands synced locally!")
        await ctx.reply("Commands synced locally!")
        
    @commands.command(name="globalsync", description="Sync all commands globally.")
    async def globalsync(self, ctx: commands.Context):
        print(f"Attempting to sync commands globally...")
        await self.bot.tree.sync()
        # await self.bot.tree.sync()
        # print(await self.bot.tree.sync(guild=ctx.guild)) #debug
        await ctx.reply("Commands synced globally!")

    @commands.command()
    async def link(self, ctx, twitchName: str):
        conn = mainConnection()
        discordName: str = ctx.author.name + '#' + ctx.author.discriminator
        conn.addLinkedAccount(twitchName, discordName)
        await ctx.send(f"Successfully linked {ctx.author} to {twitchName}!")

    @commands.command()
    async def accounts(self, ctx):
        conn = mainConnection()
        accounts = conn.getAccounts()
        for account in accounts:
            # await ctx.send(" - ".join(list(account)))
            await ctx.send(account)
        conn.close()

    @commands.command()
    async def embed(self, ctx):
        embed = embeds.queuedSongs(3)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Testing(bot))