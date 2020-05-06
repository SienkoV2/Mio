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

from typing import Iterator

from discord.ext.commands import Cog, Group, command

from utils.formatters import ColoredEmbed
from config import GITHUB_LINK


class BotInfoCog(Cog, name='Infos'):   
    __slots__ = ('bot', '_embed')
         
    def __init__(self, bot):
        self.bot = bot 
    
    @command(name='source')
    async def source(self, ctx):
        """Show the bot's source code"""
        await self.bot.wait_until_ready()
        owner = self.bot.get_user(self.bot.owner_id)
        await owner.send(f'{ctx.author} used the source command in {ctx.channel.mention},' 
                         'hope that he gave a star')
        
        await ctx.display(content=GITHUB_LINK)
    
    @command(name='stats')
    async def stats(self, ctx):
        """Shows some stats about the bot"""
        guilds, channels, members = [*self._members_stats()]
        cogs, groups, commands = [*self._bot_stats()]
        embed = ColoredEmbed(title='Stats')

        fields = [('Guilds', f'{guilds} guilds'), 
                  ('Channels', f'{channels} channels'), 
                  ('Members', f'{members} members'),
                  ('Cogs', f'{cogs} cogs'),
                  ('Groups', f'{groups} groups'),
                  ('Commands', f'{commands} commands')]
        
        for name, value in fields:
            embed.add_field(name=name, value=value)
        
        await ctx.display(embed=embed)    
    
    def _members_stats(self) -> Iterator[int]:
        """Async iterators good"""
        for container in (self.bot.guilds, self.bot.get_all_channels(), self.bot.get_all_members()):
            yield sum(1 for _ in container)
        
    def _bot_stats(self):
        """Async iterators good"""        
        groups = (c for c in self.bot.walk_commands() if isinstance(c, Group))
        for container in (self.bot.cogs, groups, self.bot.walk_commands()):
            yield sum(1 for _ in container)
                                
        
def setup(bot):
    bot.add_cog(BotInfoCog(bot))
