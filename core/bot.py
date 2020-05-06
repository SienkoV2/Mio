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
from asyncio import all_tasks
from aiohttp import ClientSession as AioClientSession
from traceback import print_exception, format_exception

from discord import HTTPException, ClientException
from discord.ext.commands import (AutoShardedBot, CooldownMapping, BucketType, 
                                  CommandOnCooldown, CommandError)

from core.ctx import NewCtx
from utils.formatters import ColoredEmbed
from config import GLOBAL_USER_COOLDOWN, EXTENSION_LOADER_PATH


class MioBot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        print('-' * 50)
        self.session = AioClientSession()
        
        for attr in ('_command_cd', '_error_cd', '_clock_cd', '_warn_cd'):
            setattr(self, attr, CooldownMapping.from_cooldown(1, GLOBAL_USER_COOLDOWN, BucketType.member))

        for env in ('JISHAKU_NO_UNDERSCORE', 'JISHAKU_NO_UNDERSCORE'):
            environ[env] = 'true'

        for ext in ('jishaku', EXTENSION_LOADER_PATH):
            self.load_extension(ext)    
                    
    # anti spam
    async def invoke(self, ctx):
        if ctx.command is None or not await self.can_run(ctx, call_once=True):
            return
        self.dispatch('command', ctx)
        try:            
            command_bucket = self._command_cd.get_bucket(ctx.message)
    
            if command_bucket.update_rate_limit() and not await ctx.is_owner():
                return self.dispatch('global_cooldown', ctx, '_clock_cd', '⏰')
            
            await ctx.command.invoke(ctx)
                
        except CommandError as exc:
            
            command_bucket.reset()    
            
            self._clock_cd.get_bucket(ctx.message).reset()
            
            await ctx.command.dispatch_error(ctx, exc)
            
        else:
            self.dispatch('command_completion', ctx)
            
    async def on_global_cooldown(self, ctx, cd_name: str, emoji: str):
        """dispatches cds for clock and warns"""
        if not getattr(self, cd_name).get_bucket(ctx.message).update_rate_limit():
            await ctx.add_reaction(emoji)
    
    async def on_command_error(self, ctx, error):
        """Overrides the default error handler"""
        if self._error_cd.get_bucket(ctx.message).update_rate_limit():
            return self.dispatch('global_cooldown', ctx, '_warn_cd', '⚠️')  
        
        error = getattr(error, 'original', error)
        
        is_owner = await ctx.is_owner()
        e_args = (type(error), error, error.__traceback__, 4)  
        
        if not isinstance(error, (HTTPException, ClientException, CommandOnCooldown)):
            print_exception(*e_args)
                
        # Cooldown bypass 
        if (isinstance(error, CommandOnCooldown)  # there must be a better way
            and (is_owner or ctx.permissions_for(ctx.author).manage_messages)):
            return await ctx.reinvoke()
        
        if is_owner:
            lines = ''.join(format_exception(*e_args))        
        else:
            lines = str(error)
        
        await ctx.display(embed=ColoredEmbed(title='Error',
                                             description='```py\n' + lines + '```'))
        
    # Custom context
    async def get_context(self, message, *, cls=NewCtx):
        """Overrides the default Ctx"""
        return await super().get_context(message, cls=cls)
            
    # close the bot properly 
    async def close(self):
        for task in all_tasks(loop=self.loop):
            await task.cancel()
        self.session.close()
        return super().close()
    