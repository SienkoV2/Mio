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

from config import BOOTUP_CHANNEL


class MioInfo(commands.Cog):
    def __init__(self, mio):
        self.mio = mio 
        mio.loop.create_task(self._fetch_github_embed())
    
    @commands.command(name='source')
    async def source(self, ctx):
        """Show Mio's source code"""
        self.embed.color = self.mio.color
        await ctx.display(embed=self.embed)
    
    @commands.command(name='stats')
    async def stats(self, ctx):
        """Shows some stats about the bot"""
        guilds, channels, members = [n async for n in self._get_numbers()]
        embed = discord.Embed(title='Stats', color=self.mio.color)

        fields = [('Guilds', f'{guilds} guilds'), 
                  ('Channels', f'{channels} channels'), 
                  ('Members', f'{members} members')]
        
        for name, value in fields:
            embed.add_field(name=name, value=value)
        
        await ctx.display(embed=embed)    
    
    async def _get_numbers(self) -> Iterator[int]:
        """Async iterators good"""
        mio = self.mio
        for container in (mio.guilds, mio.get_all_channels(), mio.get_all_members()):
            yield sum(1 for _ in container)
        
        
        

                    
                    
                    
    async def _fetch_github_embed(self):
        """For some reasons, it gets autoformatted when refetching it"""
        link = 'https://github.com/Saphielle-Akiyama/Mio'
        await self.mio.wait_until_ready()
        msg = await self.mio.get_channel(BOOTUP_CHANNEL).send(link)
        await sleep(5)
        msg_w_embed = await msg.channel.fetch_message(msg.id)
        await msg.delete()
        self.embed = msg_w_embed.embeds[0]
        
        
        
def setup(mio):
    mio.add_cog(MioInfo(mio))