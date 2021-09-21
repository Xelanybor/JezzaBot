import discord
from discord.ext import commands

from ..sql.MainConnection import mainConnection

class Testing(commands.Cog):
    """Testing commands cause idk what I'm doing lol."""

    def __init__(self, client):
        super().__init__
        self.client = client

    @commands.command()
    async def test(self, ctx):
        await ctx.send("yep it works")

    @commands.command()
    async def link(self, ctx, twitchName: str):
        conn = mainConnection()
        discordName: str = ctx.author.name + '#' + ctx.author.discriminator
        conn.addLinkedAccount(twitchName, discordName)
        await ctx.send(f"Successfully linked {ctx.author} to {twitchName}!")

    @commands.command()
    async def getAccounts(self, ctx):
        conn = mainConnection

def setup(client):
    client.add_cog(Testing(client))