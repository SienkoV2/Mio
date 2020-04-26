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
                       
        

    
    async def _fetch_github_embed(self):
        link = "https://github.com/Saphielle-Akiyama/Mio"
        await self.mio.wait_until_ready()
        msg = await self.mio.get_channel(BOOTUP_CHANNEL).send(link)
        msg_w_embed = await msg.channel.fetch_message(msg.id)
        await msg.delete()
        self.embed = msg_w_embed.embeds[0]
        
        
        
def setup(mio):
    mio.add_cog(MioInfo(mio))