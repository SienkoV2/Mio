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

from discord import Embed, Color
from discord.ext.commands import (AutoShardedBot, CommandNotFound, 
                                  CooldownMapping, BucketType, 
                                  UserInputError, CheckFailure)

from core.ctx import MioCtx
from config import GLOBAL_USER_COOLDOWN

class MioBot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users_on_cd = set()
        self.user_got_reaction = set()
        self.load_all_extensions()
        self.setup_jishaku()
        
    # bootup
    def setup_jishaku(self):
        for env in ('JISHAKU_NO_UNDERSCORE', 'JISHAKU_NO_UNDERSCORE'):
            environ[env] = 'true'
        self.load_extension('jishaku')
        
    def load_all_extensions(self):
        for file in Path('cogs').glob('**/*.py'):
            *tree, _ = file.parts
            try:
                self.load_extension(f"{'.'.join(tree)}.{file.stem}")
            except Exception as exception:
                print_exception(type(exception), 
                                exception, 
                                exception.__traceback__, 
                                file=stderr)
                
    # overriding some defaults
    async def process_commands(self, msg): 
        author = msg.author     
        if author.bot:
            return
        
        if author.id in self.users_on_cd:
            if author.id not in self.user_got_reaction:
                self.user_got_reaction.add(author.id)
                self.loop.create_task(msg.add_reaction('⏰'))
            return
        
        ctx = await self.get_context(msg)
        await self.invoke(ctx)
        
        if not ctx.command_failed and ctx.command:
            self.users_on_cd.add(author.id)
            self.loop.create_task(self.remove_cd(author.id))
            
    async def remove_cd(self, user_id : int):
        await sleep(GLOBAL_USER_COOLDOWN)
        for container in (self.users_on_cd, self.user_got_reaction):
            container.discard(user_id)
        
    async def get_context(self, message, *, cls = MioCtx):
        """Overrides the default Ctx"""
        return await super().get_context(message, cls=cls)
    
    async def on_command_error(self, ctx, exception):
        """Overrides the default error handler"""
        error = getattr(exception, "original", exception)
        if isinstance(error, CommandNotFound):
            return
        
        e_args = (type(exception), exception, exception.__traceback__)
        
        if not isinstance(error, (UserInputError, CheckFailure)):
            print_exception(*e_args, file=stderr)
        
        verbosity = 1
        if (is_owner := await self.is_owner(ctx.author)):
            verbosity += 7
            
        lines = ''.join(format_exception(*e_args, 4))
        
        await ctx.display(embed=Embed(title=f'Error : {type(exception).__name__}',
                                      color=self.color,
                                      description=f"```py\n{lines}```"))
        
    @property
    def color(self):
        return Color.from_hsv(random(), uniform(0.75, 0.95), 1)
        
    # Log stuff
    def load_extension(self, name):
        super().load_extension(name)
        print(f"{'-'*50}\nLoaded extension : {name}")
        
    def unload_extension(self, name):
        super().unload_extension(name)
        print(f"{'-'*50}\nUnloaded extention : {name}")
                
    def reload_extension(self, name):
        super().reload_extension(name)
        print(f"{'-'*50}\nReloaded extension : {name}")
    
