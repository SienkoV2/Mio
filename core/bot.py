from os import environ
from sys import stderr
from pathlib import Path
from random import random, uniform
from traceback import print_exception, format_exception

from discord import Embed, Color
from discord.ext.commands import AutoShardedBot, CommandNotFound

from core.ctx import MioCtx

class MioBot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_all_extensions()
        self.setup_jishaku()
        
    def setup_jishaku(self):
        for env in ('JISHAKU_NO_UNDERSCORE', 'JISHAKU_NO_UNDERSCORE'):
            environ[env] = 'true'
        self.load_extension('jishaku')
        
    # bootup
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
    async def get_context(self, message, *, cls = MioCtx):
        return await super().get_context(message, cls=cls)
    
    async def on_command_error(self, ctx, exception):
        error = getattr(exception, "original", exception)
        if isinstance(error, CommandNotFound):
            return
        
        e_args = (type(exception), exception, exception.__traceback__)
        print_exception(*e_args, file=stderr)
        
        verbosity = 1
        if (is_owner := await self.is_owner(ctx.author)):
            verbosity += 7
            
        lines = '\n'.join(format_exception(*e_args, 4))
        
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
    