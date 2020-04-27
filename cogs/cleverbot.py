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

from discord import Message
from discord.ext.commands import Cog

import async_cleverbot as ac

from config import TRAVITIA_TOKEN


from random import choice

class Cleverbot(Cog):
    def __init__(self, mio):
        self.mio = mio
        
        self.cb_client = ac.Cleverbot(TRAVITIA_TOKEN)
        self.cb_client.set_context(ac.DictContext(self.cb_client))
        
    @Cog.listener()
    async def on_message(self, msg : Message):        
        ctx = await self.mio.get_context(msg)
        if (msg.author.bot or ctx.command
            or not (self.mio.user.mentioned_in(msg) or msg.guild is None)):
            return
        
        self.mio.loop.create_task(ctx.trigger_typing())
              
        emotion = ac.Emotion.angry if msg.mention_everyone else ac.Emotion.happy
              
        cb_ans = await self.cb_client.ask(msg.content, 
                                          id_=msg.author.id, 
                                          emotion=emotion)
        
        f_ans = f"{ctx.author.mention} {cb_ans.text}" if ctx.guild is not None else cb_ans.text
        await ctx.send(f_ans)
        
    async def cog_unload(self):
        """Calls the func to close the aiohttp session"""
        self.mio.loop.create_task(close())
        
    async def close(self):
        """Closes the aiohttp session."""
        await self.cb_client.session.close()
        
def setup(mio):
    mio.add_cog(Cleverbot(mio))
    