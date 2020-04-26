import discord
from discord.ext import commands
from utils.interfaces import ShortPaginator

class Test(commands.Cog):
    def __init__(self, mio):
        self.mio = mio
        
    @commands.command()
    async def test(self, ctx, n : int):
        pag = ShortPaginator(ctx, embeds=[discord.Embed(title='Hello') for _ in range(n)])
        await pag.run_until_complete()




def setup(mio):
    mio.add_cog(Test(mio))
