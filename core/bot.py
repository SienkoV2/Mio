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
from traceback import print_exception, format_exception

from discord.ext.commands import (AutoShardedBot, CooldownMapping, BucketType, 
                                  UserInputError, CheckFailure, CommandOnCooldown,
                                  CommandError, NotOwner, MaxConcurrencyReached)

from utils.formatters import ColoredEmbed
from core.ctx import NewCtx
from config import GLOBAL_USER_COOLDOWN, EXTENSION_LOADER_PATH


class MioBot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_defaults()

        for attr in ('_command_cd', '_error_cd', '_clock_cd', '_warn_cd'):
            cd_args = (1, GLOBAL_USER_COOLDOWN, BucketType.member)
            cd = CooldownMapping.from_cooldown(*cd_args)
            setattr(self, attr, cd)

    # bootup
    def _setup_defaults(self):
        """Loads Jishaku and the extension loader"""
        print('-' * 50)
        for env in ('JISHAKU_NO_UNDERSCORE', 'JISHAKU_NO_UNDERSCORE'):
            environ[env] = 'true'

        for ext in ('jishaku', EXTENSION_LOADER_PATH):
            self.load_extension(ext)    
            
    # anti spam
    async def invoke(self, ctx):
        if ctx.command is None:
            return
        
        self.dispatch('command', ctx)
        try:
            if await self.can_run(ctx, call_once=True):
                
                is_owner = await self.is_owner(ctx.author)
                
                command_bucket = self._command_cd.get_bucket(ctx.message)
                retry_after = command_bucket.update_rate_limit()
                
                if retry_after and not is_owner:
                    return self.dispatch('global_cooldown', ctx, '_clock_cd', '⏰')
                
                await ctx.command.invoke(ctx)
                
        except CommandError as exc:
            
            command_bucket.reset()    
            
            self._clock_cd.get_bucket(ctx.message).reset()
            
            retry_after = self._error_cd.get_bucket(ctx.message).update_rate_limit()
            
            # owner only commands are hidden 
            if retry_after and not is_owner and not isinstance(exc, NotOwner):
                return self.dispatch('global_cooldown', ctx, '_warn_cd', '⚠️')  
            
            await ctx.command.dispatch_error(ctx, exc)
            
        else:
            self.dispatch('command_completion', ctx)

    async def on_global_cooldown(self, ctx, cd_name: str, emoji: str):
        """dispatches cds for clock and warns"""
        if not getattr(self, cd_name).get_bucket(ctx.message).update_rate_limit():
            await ctx.add_reaction(emoji)


                                        
    
    async def on_command_error(self, ctx, error):
        """Overrides the default error handler"""
        error = getattr(error, 'original', error)
        
        await ctx.display(content=error)
                            
    # Custom context
    async def get_context(self, message, *, cls=NewCtx):
        """Overrides the default Ctx"""
        return await super().get_context(message, cls=cls)
    
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