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

from re import findall
from typing import Union, Iterable

from discord import Embed
from discord.ext.commands import (EmojiConverter, PartialEmojiConverter, 
                                  BadArgument, Context)

from utils.interfaces import autodetect

class NewCtx(Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        
    async def add_reaction(self, emoji):
        """Adds an emoji to the original message"""
        await self.message.add_reaction(emoji)
    
    async def display(self, **options):
        """Automatically detects which paginator to use"""
        return await autodetect(ctx=self, **options).run_until_complete()
    
    async def emojis(self):
        """Finds all custom emojis"""
        msg_txt = self.message.content
        for emoji in findall(r'<a?:[a-zA-Z0-9\_]+:([0-9]+)>$', msg_txt):
            try:
                emoji = await EmojiConverter().convert(self, msg_txt)
            except BadArgument:
                emoji = await PartialEmojiConverter().convert(self, msg_txt)
            finally:
                yield emoji
                
                
                