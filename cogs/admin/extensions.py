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


from typing import Union
from pathlib import Path
from typing import Tuple, Callable, Iterable

from discord.ext.commands import Cog, NotOwner, group

from utils.formatters import ColoredEmbed, chunker
from config import EXTENSION_LOADER_PATH


class ExtensionLoadingCog(Cog, name='Admin'):
    __slots__ = ('bot',)
    
    def __init__(self, bot):
        self.bot = bot
        if len(bot.extensions) <= 1:
            self.bot.loop.create_task(self.extensions_load(None, None))
        
    @group(name='extensions', aliases=['ext', '-e'], invoke_without_command=True)
    async def extensions_(self, ctx):
        """Extensions managing commands"""
        embeds = []
        for chunk in chunker([v for v in self.bot.cogs.values()]):
            embed = ColoredEmbed(title=f"{self.bot.user}'s cogs")
            for cog in chunk:
                f_value = f"{len(cog.get_commands())} command(s), {len(cog.get_listeners())} listener(s)"
                embed.add_field(name=cog.qualified_name, value=f_value, inline=False)
            embeds.append(embed)
            
        await ctx.display(embeds=embeds)
        
    @extensions_.command(name='load', aliases=['-l'])
    async def extensions_load(self, ctx, query: str = None):
        """
        Loads all extensions matching the query
        """
        report = self._manage(self.bot.load_extension, self._get_ext_path(query))
        
        if ctx is None:  # On bootup, execute this func with None everywhere
            return print(*report, sep='\n')
        
        if (embeds:= [*self._format('Loaded extensions', report)]):
            await ctx.display(embeds=embeds)
        else:
            await ctx.display(embed=ColoredEmbed(title="Couldn't find any matching extensions"))

    @extensions_.command(name='reload', aliases=['re', '-r'])
    async def extension_reload(self, ctx, query: str = None):
        """
        Reloads all extensions matching the query
        """
        exts = [e for e in self.bot.extensions if query in e.split('.') + [None]]
        
        report = self._manage(self.bot.reload_extension, exts)
        
        if (embeds:= [*self._format('Reloaded extensions', report)]):
            await ctx.display(embeds=embeds)
        else:
            await ctx.display(embed=ColoredEmbed(title="Couldn't find any matching extensions"))
            
    @extensions_.command(name='unload', aliases=['un', '-u'])
    async def extensions_unload(self, ctx, query: str = None):
        """
        Unloads all extensions matching the query 
        """        
        exts = [e for e in self.bot.extensions if (query in e.split('.') + [None]) and e != 'jishaku']
        
        report = self._manage(self.bot.unload_extension, exts)
        
        if (embeds:= [*self._format('Unloaded extensions', report)]):
            await ctx.display(embeds=embeds)
        else:
            await ctx.display(embed=ColoredEmbed(title="Couldn't find any matching extensions"))
        
    async def cog_before_invoke(self, ctx):
        """Owner only cog"""
        if not await self.bot.is_owner(ctx.author):  # silent error
            message = 'You must own this bot to load extensions'
            raise NotOwner(message=message)
            
    def _format(self, action: str, 
                report: Iterable[Tuple[str, str]]) -> Iterable[ColoredEmbed]:
        """Formats embeds to show which extensions errored out"""        
        for chunk in chunker([*report]):
            embed = ColoredEmbed(title=action)
            for cog, message in chunk:
                embed.add_field(name=cog, value=f"```py\n{message}```", inline=False)
                
            yield embed
        
    def _manage(self, func: Callable, iterable: Iterable) -> Iterable[Tuple[str, str]]:
        """Loads / reloads / unloads extensions"""        
        for ext in iterable:
            try:
                func(ext)
            except Exception as e:
                yield (ext, str(e))
            else:
                yield (ext,'No error')
                    
    def _get_ext_path(self, query: Union[str, None]) -> Iterable[Path]:
        """
        Gets all py files in the cogs folder
        that corresponds to the query
        """        
        for file in Path('cogs').glob('**/*.py'):
            *tree, _ = file.parts
            if query in (tree + [None]):
                yield f"{'.'.join(tree)}.{file.stem}"


def setup(bot):
    bot.add_cog(ExtensionLoadingCog(bot))
