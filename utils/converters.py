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

from discord import NotFound
from discord.ext.commands import Converter, UserConverter, BadArgument, MessageConverter


class FetchedUser(Converter):
    __slots__ = tuple()
    
    """Finds an user from name/id, fetches it if needed"""
    async def convert(self, ctx, arg):
        try:
            return await UserConverter().convert(ctx, arg)
        except BadArgument:
            try:
                id_ = int(arg)
            except ValueError:
                raise BadArgument(f"Couldn't find an user named {arg}")
            else:
                return await ctx.bot.fetch_user(id_)


class AnyToUser(Converter):
    __slots__ = tuple()
    
    """
    Tries to find an user, includes msg ids too
    Doesn't raise any error if it couldn't find it
    """
    async def convert(self, ctx, arg):
        # tries to find from an user  
        user = await self.from_user(ctx, arg)
        if user is not None: 
            return user
    
        # tries to find from a message id 
        message = await self.from_message(ctx, arg)
        if message is not None: 
            return message.author
        
        # out of ideas, raising no errors
        return None
        
    async def from_user(self, ctx, arg):
        try:
            return await FetchedUser().convert(ctx, arg)
        except NotFound:
            return None
        
    async def from_message(self, ctx, arg):
        try:
            return await MessageConverter().convert(ctx, arg)
        except BadArgument:
            return None
        