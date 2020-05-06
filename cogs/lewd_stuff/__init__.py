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

from discord.ext.commands import Cog, command, is_nsfw
from cogs.lewd_stuff.doujins import format_nhentai_pages, ColoredEmbed, PaginatorDoujinReader


class NsfwCog(Cog, name='Nsfw'):
    
    def __init__(self, bot):
        self.bot = bot  
        
    @command(name='nhentai')
    @is_nsfw()
    async def nhentai_(self, ctx, query: DoujinshiConverter):
        if not (pages:= [p async for p in format_nhentai_pages(query)]):
            return await ctx.display(embed=ColoredEmbed(title='No doujin found'))    
        else:
            await PaginatorDoujinReader(ctx=ctx, embeds=pages, doujins=query).run_until_complete()  
       


    
def setup(bot):
    bot.add_cog(NsfwCog(bot))
