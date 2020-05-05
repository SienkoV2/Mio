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

import discord
from discord.ext import commands


class UserModerationCog(commands.Cog, name='Moderation'):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.commands(name='kick')
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], reason: str = None):
        for member in members:
            try:
                await member.ban(reason=reason)
            except discord.HTTPException:
                pass
            
    @commands.command(name='ban')
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], reason: str = None, delete_message_days: int = 1):
        for member in members:
            try:
                await member.ban(reason=reason, delete_message_days=delete_message_days)
            except discord.HTTPException:
                pass
    
    @commands.commands(name='unban') 
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, members: commands.Greedy[discord.Member], reason: str = None):
        for member in members:
            try:
                await member.ban(reason=reason)
            except discord.HTTPException:
                pass
           
        
        
def setup(bot):
    bot.add_cog(UserModerationCog(bot))