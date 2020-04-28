import discord
from discord.ext import commands

class RockPaperScissorCog(commands.Cog, name='Games'):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.send('Hello')
    
    @commands.command(name='world')
    async def world(self, ctx):
        await ctx.send('World')    
    
    @commands.command(name='hahayes')
    async def hahayes(self, ctx):
        await ctx.send('hahayes')
   
def setup(bot):
    bot.add_cog(RockPaperScissorCog(bot))
