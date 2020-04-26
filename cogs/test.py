import discord
from discord.ext import commands
from utils.interfaces import ShortPaginator

class Test(commands.Cog):
    def __init__(self, mio):
        self.mio = mio
        
    @commands.command()
    async def test(self, ctx, n : int):
        appinfo = await ctx.bot.application_info()

        embed = discord.Embed(title='Hello', color=ctx.bot.color)

        for attr_name in dir(appinfo):
            attr = getattr(appinfo, attr_name)
            print(attr)

        return await ctx.send(embed=embed)




def setup(mio):
    mio.add_cog(Test(mio))
