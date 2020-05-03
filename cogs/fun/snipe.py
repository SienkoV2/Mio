"""
MIT License

Copyright (c) 2020 Saphielle Akiyama

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__title__ = 'Mio'
__author__ = 'Saphielle-Akiyama'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020 Saphielle-Akiyama'

import discord
from discord.ext.commands import Cog, command
from utils.formatters import ColoredEmbed

class SnipeCog(Cog, name='Fun'):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self._prepare_cache())
        
    async def _prepare_cache(self):
        await self.bot.wait_until_ready()   
        self.snipes = {g.id : {} for g in self.bot.guilds}  

    @commands.Cog.listener()
    async def on_guild_join(self, guild): 
        self.snipes[guild.id] = {}
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild): 
        self.snipes.pop(guild.id)
        
    @commands.Cog.listener()
    async def on_message_delete(self, msg : discord.Message):
        """Main listener"""
        await self.bot.wait_until_ready()
        if not msg.author.bot:
            self.snipes[msg.guild.id][msg.channel.id] = msg
        
    @command(name='snipe')
    async def snipe(self, ctx):
        msg = self.snipes[ctx.guild.id].get(ctx.channel.id, None)
        if msg is None:
            content = "Couldn't find any sniped messages in this channel"
            return await ctx.send(content=content, delete_after=5)
        
        embed = ColoredEmbed(title=f'Sniped a message from {msg.author}',
                             description=msg.content)
        
        await ctx.display(embed=embed)
        
        
    
def setup(bot):
    bot.add_cog(SnipeCog(bot))