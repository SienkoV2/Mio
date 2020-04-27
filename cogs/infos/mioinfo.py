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
from typing import Iterator
from asyncio import sleep

import discord
from discord.ext import commands

from config import BOOTUP_CHANNEL, GITHUB_LINK


class MioInfoCog(commands.Cog):        
    def __on_cog_load(self, bot):
        self.bot = bot 
        self.bot.loop.create_task(self.__fetch_github_embed())
    
    def cog_unload(self):
        print('unloaded')
    
    
    @commands.command(name='source')
    async def source(self, ctx):
        """Show Mio's source code"""
        await self.bot.wait_until_ready()
        self.__embed.color = self.bot.color
        await ctx.display(embed=self.__embed)
    
    @commands.command(name='stats')
    async def stats(self, ctx):
        """Shows some stats about the bot"""
        guilds, channels, members = [n async for n in self._members_stats()]
        cogs, groups, commands = [n async for n in self._bot_stats()]
        embed = discord.Embed(title='Stats', color=self.mio.color)

        fields = [('Guilds', f'{guilds} guilds'), 
                  ('Channels', f'{channels} channels'), 
                  ('Members', f'{members} members'),
                  ('Cogs', f'{cogs} cogs'),
                  ('Groups', f'{groups} groups'),
                  ('Commands', f'{commands} commands')]
        
        for name, value in fields:
            embed.add_field(name=name, value=value)
        
        await ctx.display(embed=embed)    
    
    async def __members_stats(self) -> Iterator[int]:
        """Async iterators good"""
        mio = self.mio
        for container in (mio.guilds, mio.get_all_channels(), mio.get_all_members()):
            yield sum(1 for _ in container)
        
    async def __bot_stats(self):
        """Async iterators good"""
        groups = filter(lambda c : isinstance(c, commands.Group), self.mio.walk_commands())
        for container in (self.mio.cogs, groups, self.mio.walk_commands()):
            yield sum(1 for _ in container)
                                
    async def __fetch_github_embed(self):
        await self.bot.wait_until_ready()
        channel = await self.bot.fetch_channel(BOOTUP_CHANNEL)
        msg = await channel.send(GITHUB_LINK)
        await sleep(2)
        msg_with_embed = await channel.fetch_message(msg.id)
        await msg.delete()
        self.__embed = msg_with_embed.embeds[0]