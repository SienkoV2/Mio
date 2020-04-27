import discord
from discord.ext import commands
from utils.interfaces import ShortPaginator

class Test(commands.Cog):
    def __init__(self, mio):
        self.mio = mio
        
    @commands.command()
    async def test(self, ctx, amount : int = 5):
        await ctx.display(embeds=[discord.Embed(title='hello') for _ in range(amount)])




def setup(mio):
    mio.add_cog(Test(mio))
