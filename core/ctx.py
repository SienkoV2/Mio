from re import findall
from typing import Union, Iterable

from discord import Embed
from discord.ext.commands import EmojiConverter, PartialEmojiConverter, BadArgument, Context
from utils.interfaces import autodetect

class MioCtx(Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        
    async def add_reaction(self, emoji):
        """Adds an emoji to the original message"""
        await self.message.add_reaction(emoji)
    
    async def display(self, **options):
        """Directly calls the autodetect function"""
        interface = await autodetect(self, **options)
        await interface.run_until_complete()
    
    async def emojis(self):
        msg_txt = self.message.content
        for emoji in findall(r'<a?:[a-zA-Z0-9\_]+:([0-9]+)>$', msg_txt):
            try:
                emoji = await EmojiConverter().convert(self, msg_txt)
            except BadArgument:
                emoji = await PartialEmojiConverter().convert(self, msg_txt)
            finally:
                yield emoji