import discord
from discord.ext import commands

class Testing(commands.Cog):
    """Testing commands cause idk what I'm doing lol."""

    def __init__(self, client):
        super().__init__
        self.client = client

    @commands.command()
    async def test(self, ctx):
        await ctx.send("yep it works")

def setup(client):
    client.add_cog(Testing(client))