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
from pathlib import Path
from asyncio import sleep
from random import random, uniform
from traceback import print_exception, format_exception

from discord import Color
from discord.ext.commands import (AutoShardedBot, CommandNotFound, 
                                  CooldownMapping, BucketType, 
                                  UserInputError, CheckFailure,
                                  CommandError, NotOwner)

from utils.formatters import ColoredEmbed
from core.ctx import NewCtx
from config import GLOBAL_USER_COOLDOWN, EXTENSION_LOADER_PATH

class MioBot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cd = CooldownMapping.from_cooldown(1.0, 5.0, BucketType.user)
        self._clocks = set()
        self._setup_default()
        
    # bootup
    def _setup_default(self):
        for env in ('JISHAKU_NO_UNDERSCORE', 'JISHAKU_NO_UNDERSCORE'):
            environ[env] = 'true'
            
        for ext in ('jishaku', EXTENSION_LOADER_PATH):
            self.load_extension(ext)    
                            
    # overriding some defaults
    async def invoke(self, ctx):
        """Adds a silent cooldown on all commands"""
        if ctx.command is not None:
            self.dispatch('command', ctx)
            try:
                if await self.can_run(ctx, call_once=True):
                    
                    bucket = self._cd.get_bucket(ctx.message)
                    retry_after = bucket.update_rate_limit()
                    if retry_after and not await self.is_owner(ctx.author): 
                        return await self._dispatch_clock(ctx)
                    
                    self._clocks.discard(ctx.author.id)
                    
                    await ctx.command.invoke(ctx)
                    
            except CommandError as exc:
                self._clocks.discard(ctx.author.id) ; bucket.reset()
                await ctx.command.dispatch_error(ctx, exc)
            else:
                self.dispatch('command_completion', ctx)
                
    async def _dispatch_clock(self, ctx):
        id_ = ctx.author.id
        if id_ not in self._clocks:
            await ctx.add_reaction('⏰')
            self._clocks.add(id_)        
                
    async def get_context(self, message, *, cls=NewCtx):
        """Overrides the default Ctx"""
        return await super().get_context(message, cls=cls)
    
    async def on_command_error(self, ctx, exception):
        """Overrides the default error handler"""
        error = getattr(exception, "original", exception)
        if isinstance(error, (CommandNotFound, NotOwner)):
            return
        
        e_args = (type(exception), exception, exception.__traceback__)
        
        if not isinstance(error, (UserInputError, CheckFailure)):
            print_exception(*e_args, file=stderr)
        
        if await self.is_owner(ctx.author):
            lines = ''.join(format_exception(*e_args, 4))
        else:
            lines = str(exception)
        
        embed = ColoredEmbed(title=f'Error : {type(exception).__name__}',
                             description=f"```py\n{lines}```")
        
        await ctx.display(embed=embed)
                            
    # Log stuff
    def load_extension(self, name):
        super().load_extension(name)
        print(f"Loaded extension : {name}\n{'-'*50}")
        
    def unload_extension(self, name):
        super().unload_extension(name)
        print(f"Unloaded extention : {name}\n{'-'*50}")
                
    def reload_extension(self, name):
        super().reload_extension(name)
        print(f"Reloaded extension : {name}\n{'-'*50}")
    
