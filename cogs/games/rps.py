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
from discord.ext import commands
from utils.miodisplay import MioDisplay, button
from asyncio import gather

class RockPaperScissorCog(commands.Cog, name='Games'):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='rps')
    async def rps(self, ctx, opponent : discord.Member = None):
        if opponent is None:
            title = f'React to duel {ctx.author} in a rock paper scissor duel'
            embed = discord.Embed(title=title, color=self.bot.color)    
            result = await ChooseAnyoneMenu(ctx, embed=embed)
            opponent = result.member
            
        else:
            title = f'{ctx.author} asked you to join a rock paper scissor duel'
            embed = discord.Embed(title=title, color=self.bot.color)
            result = await AcceptMenu(ctx, embed=embed, content=opponent.mention)
            opponent = result.member
           
        if opponent is None:
            embed = discord.Embed(title='No one accepted the duel',
                                  color=self.bot.color)
            
            return await ctx.display(embed=embed)
        
        embed = discord.Embed(title='Pick an object using the reaction !')
        menu = RpsMenu(ctx, channel=ctx.author)
        
        results = await gather()
        
            
            
    
   
   


class RpsMenu(MioDisplay):
    @button(emoji='🗿', position=0)
    async def on_rock(self, payload):
        self.choice = 'rock'
        
    @button(emoji='📝', position=1)
    async def on_paper(self, payload):
        self.choice = 'paper'

    @button(emoji='✂️', position=1)
    async def on_scissor(self, payload):
        self.choice = 'scissor'

class AcceptMenu(MioDisplay):
    @button(emoji='✅', position=0)
    async def on_green_tick(self, payload):
        self.member = payload.member
    
    @button(emoji='❌', position=1)
    async def on_cross_mark(self, payload):
        self.member = None

class ChooseAnyoneMenu(MioDisplay):
    def __init__(self, ctx, **options):
        super().__init__(ctx, **options)
        self.member = None
        
    @button(emoji='🎲', position=0)
    async def on_die(self, payload):
        self.user_id = payload.member
        
    async def after(self):
        await self.msg.delete()   
        await self.ctx.add_reaction('🍓') 
   
   
def setup(bot):
    bot.add_cog(RockPaperScissorCog(bot))
