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

from typing import Union, List, Optional

import discord
from discord.ext.commands import Converter, Cog, command, is_nsfw

from humanize import naturaldate

from nhentai.nhentai import Doujinshi
from nhentai.nhentai import search as n_search

import rule34

from utils.formatters import ColoredEmbed
from utils.interfaces import Paginator, button


#! Nhentai 
        
class DoujinshiConverter(Converter):
    __slots__ = tuple()
    
    """Converts a query into Doujinshi obj"""
    async def convert(self, ctx, arg: str) -> Doujinshi:
        try:
            query = int(arg)
        except ValueError:
            return await ctx.bot.loop.run_in_executor(None, self.from_string, arg)
        else:
            return await ctx.bot.loop.run_in_executor(None, self.from_index, query)

    def from_index(self, index: int):
        return [Doujinshi(index)]
    
    def from_string(self, query: str):
        return [*n_search(query, 1)]
    
    
class PaginatorDoujinReader(Paginator):
    def __init__(self, **options):
        super().__init__(**options)
        self.original_embeds = self.embeds
        self.doujins = options.pop('doujins')

    @button(emoji='📖', position=6)
    async def on_book(self, payload):
        self.embeds = [*self._format_doujins(self.doujins[self._index])]
        self.front_page_index = self._index
        await self.goto_index('FIRST')
        
    @button(emoji='↩️', position=7)
    async def on_return(self, payload):
        self.embeds = self.original_embeds
        await self.goto_index(self.front_page_index)

    def _format_doujins(self, doujin):
        for image_url in doujin._images:
            yield ColoredEmbed(title='Reading mode', url=image_url).set_image(url=image_url)


async def format_nhentai_pages(results: List[Doujinshi]):
    for doujin in results:            
        embed = ColoredEmbed(title=f'{doujin.name} ({doujin.magic})',
                             url=f'https://nhentai.net/g/{doujin.magic}')
        
        # Cover image
        if (cover_url:= getattr(doujin, 'cover', None)):
            embed.set_image(url=cover_url)
            
        # japanese name 
        if (jname:= getattr(doujin, 'jname', None)):
            embed.add_field(name='Japanese name', value=jname, 
                            inline=False)

        # tags
        if (tags:= getattr(doujin, 'tags', None)):                 
            if [t for t in tags if t in {'loli', 'shota'}]:
                continue
            
            embed.add_field(name='Tags', 
                            value=' | '.join((f"`{t}`" for t in tags)), 
                            inline=False)
        yield embed
    
    
#! Rule34

class Rule34Client(rule34.Rule34):
    """Subclassed the client to avoid creating a new session everytime"""
    def __init__(self, bot, timeout=10):
        self.timeout = timeout
        self.loop = bot.loop
        self.session = bot.session


async def format_r34_images(r34posts: List[str]):
    """Formats the r34 posts into an embed"""
    for post in r34posts:
        embed = ColoredEmbed(title=f"Author's id : {post.creator_ID}", url=post.file_url)
        embed.set_image(url=post.file_url)
        fields = (('Created at', naturaldate(post.created_at)),
                  ('Resolution', f"{post.width} x {post.height}"))
        for name, value in fields:
            embed.add_field(name=name, value=value)
            
        yield embed


class NsfwCog(Cog, name='Nsfw'):
    def __init__(self, bot):
        self.bot = bot
        self.r34client = Rule34Client(bot)
        
    @command(name='nhentai')
    async def nhentai_(self, ctx, query: DoujinshiConverter):
        """Looks for a nhentai doujin, per index or per name and displays it"""
        if not (pages:= [p async for p in format_nhentai_pages(query)]):
            return await ctx.display(embed=ColoredEmbed(title='No doujin found'))    
        else:
            await PaginatorDoujinReader(ctx=ctx, embeds=pages, doujins=query).run_until_complete()  

    @command(name='rule34', aliases=['r34'])
    async def rule34_(self, ctx, fuzzy: Optional[bool] = True, *, query: str):
        if not (r34posts:= await self.r34client.getImages(singlePage=True, randomPID=True, 
                                                          tags=query, fuzzy=fuzzy)):
            return await ctx.display(embed=ColoredEmbed(title="Couldn't find any post matching your query"))
        else:
            await ctx.display(embeds=[e async for e in format_r34_images(r34posts)])
            
        





    

    async def cog_check(self, ctx):
        """Checks if the channel is nsfw"""
        return ctx.channel.is_nsfw()


    
def setup(bot):
    bot.add_cog(NsfwCog(bot))
