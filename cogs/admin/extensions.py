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

from os import environ
from sys import stderr
from typing import Union
from pathlib import Path
from traceback import format_exception
from typing import Tuple, List, Callable, Iterable

from discord.ext import commands

from utils.formatters import ColoredEmbed, chunker
from config import EXTENSION_LOADER_PATH

class ExtensionLoadingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.loop.create_task(self.extensions_load(None, None))
        
    @commands.group(name='extensions', aliases=['ext'], invoke_without_command=True)
    @commands.is_owner()
    async def extensions_(self, ctx):
        """Extensions managing commands"""
        await ctx.send_help(ctx.command)
        
    @extensions_.command(name='load')
    @commands.is_owner()
    async def extensions_load(self, ctx, query : str = None):
        """
        Loads all extensions matching the query
        """
        report = await self.loop.run_in_executor(None,
                                                 self._manage,
                                                 query,
                                                 self.bot.load_extension,
                                                 self._get_ext_path(query))
        
        if ctx is None: # On bootup, execute this func with None everywhere
            return [*report]
        
        await ctx.display(embeds=[*self._format('Loaded extensions', report)])
    
    @extensions_.command(name='reload', aliases=['re'])
    @commands.is_owner()
    async def extension_reload(self, ctx, query : str = None):
        """
        Reloads all extensions matching the query
        """
        report = await self.loop.run_in_executor(None,
                                                 self._manage,
                                                 query, 
                                                 self.bot.reload_extension,
                                                 (e for e in self.bot.extensions))

        await ctx.display(embeds=[*self._format('Reloaded extensions', report)])
    
    @extensions_.command(name='unload', aliases=['un'])
    @commands.is_owner()
    async def extensions_unload(self, ctx, query : str = None):
        """
        Unloads all extensions matching the query 
        """
        report = await self.loop.run_in_executor(None,
                                                 self._manage,
                                                 query,
                                                 self.bot.reload_extension,
                                                 (e for e in self.bot.extensions))
        
        await ctx.display(embeds=[*self._format('Unloaded extensions', report)])
        
            
    def _format(self, action : str, report : Iterable[Tuple[str, str]]) -> Iterable[ColoredEmbed]:
        """Formats embeds to show which extensions errored out"""        
        for chunk in chunker([*report]):
            embed = ColoredEmbed(title=action)
            for cog, message in chunk:
                embed.add_field(name=cog, value=message, inline=False)
                
            yield embed
        
    def _manage(self, 
                query : Union[str, None], 
                func : Callable,
                iterable : Iterable) -> Iterable[Tuple[str, str]]:
        """Loads / unloads extensions"""        
        for ext in iterable:
            try:
                func(ext)
            except Exception as e:
                yield (ext, str(e))
            else:
                yield (ext, 'No error')
                
    def _get_ext_path(self, query : Union[str, None]) -> Iterable[Path]:
        """
        Gets all py files in the cogs folder
        that corresponds to the query
        """        
        for file in Path('cogs').glob('**/*.py'):
            *tree, _ = file.parts
            if query in (tree + [None]):
                if (ext := f"{'.'.join(tree)}.{file.stem}") != EXTENSION_LOADER_PATH:
                    yield ext

def setup(bot):
    bot.add_cog(ExtensionLoadingCog(bot))



        
    