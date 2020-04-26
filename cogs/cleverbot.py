import discord
from discord.ext import commands

import async_cleverbot as ac
from aiogoogletrans import Translator

from config import TRAVITIA_TOKEN


class Cleverbot(commands.Cog):
    def __init__(self, mio):
        self.mio = mio
        
        self.cb_client = ac.Cleverbot(TRAVITIA_TOKEN)
        self.cb_client.set_context(ac.DictContext(self.cb_client))
        
    
    @commands.Cog.listener()
    async def on_message(self, msg : discord.Message):
        ctx = await self.mio.get_context(msg)
        if (msg.author.bot or ctx.command
            or not (self.mio.user.mentioned_in(msg) or msg.guild is None)):
            return
        
        self.mio.loop.create_task(ctx.trigger_typing())
              
        cb_ans = await self.cb_client.ask(msg.content, 
                                          id_=msg.author.id, 
                                          emotion=ac.Emotion.happy)
        
        f_ans = f"{ctx.author.mention} {cb_ans.text}" if ctx.guild is not None else cb_ans.text
        
        await ctx.send(f_ans)
        
        
def setup(mio):
    mio.add_cog(Cleverbot(mio))
    