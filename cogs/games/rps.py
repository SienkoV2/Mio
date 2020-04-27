import discord
from discord.ext import commands

class RockPaperScissorCog(commands.Cog):
    def __on_cog_load(self, bot):
        self.bot = bot
        
    @commands.command(name='rps')
    async def rps(self, ctx, opponent : discord.Member = None):
        pass
    
    