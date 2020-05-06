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

from typing import Tuple, Union

from discord import DiscordException, Member
from discord.ext.commands import (Cog, bot_has_guild_permissions, command,
                                  has_guild_permissions, Greedy)

from utils.converters import AnyToUser, FetchedUser
from utils.formatters import ColoredEmbed, chunker


class MemberModerationCog(Cog, name='Moderation'):
    __slots__ = ('bot',)
    
    def __init__(self, bot):
        self.bot = bot
        
    @command(name='kick')
    @has_guild_permissions(kick_members=True)
    @bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, reason: str = None):
        """Kicks a single member"""
        await member.kick(reason=reason)
        await self._display(ctx, 'kick', reason, member)
                
    @command(name='ban')
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: FetchedUser, reason: str = None, delete_message_days: int = 1):
        """Bans a single member"""
        await ctx.guild.ban(user, reason=reason, delete_message_days=delete_message_days)
        await self._display(ctx, 'ban', reason, user)
            
    @command(name='unban')
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx, user: FetchedUser, reason: str = None):
        """Unbans a single member"""
        await ctx.guild.unban(user, reason=reason)
        await self._display(ctx, 'unban', reason, user)
        
    async def _display(self, ctx, event_type: str, reason: str, user):
        embed = ColoredEmbed(title=event_type)
        
        fields = (('Reason', reason, False),
                  ('User', str(user), True),
                  ('Author', ctx.author.mention, True))
        
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
            
        await ctx.display(embed=embed)
        
    @command(name='masskick')
    @has_guild_permissions(kick_members=True)
    @bot_has_guild_permissions(kick_members=True)
    async def masskick(self, ctx, members: Greedy[AnyToUser]):
        """
        Kicks multiple users
        
        No reason can be provided because every argument 
        separated by a whitespace will be converted to an user
        if possible

        If a message id is copied, it's author will be selected
        """
        title = f'Mass kick by {ctx.author}'
        kicked = [k async for k in self._execute_users(ctx, members, 
                                                       action='kick', 
                                                       reason=title, 
                                                       success_word='kicked')]
        await self._display_mass(ctx, title, kicked)
                    
    @command(name='massban')
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    async def massban(self, ctx, users: Greedy[AnyToUser]):
        """
        Bans multiple users
        
        No reason can be provided because every argument 
        separated by a whitespace will be converted to an user
        if possible

        If a message id is copied, it's author will be selected
        """
        title = f'Mass ban by {ctx.author}'
        banned = [banned async for banned in self._execute_users(ctx, users,
                                                                 action='ban',
                                                                 reason=title,
                                                                 success_word='banned')]
        await self._display_mass(ctx, title, banned)
            
    @command(name='massunban')
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    async def massunban(self, ctx, users: Greedy[AnyToUser]):
        """
        Unbans multiple users
        
        No reason can be provided because every argument 
        separated by a whitespace will be converted to an user
        if possible

        If a message id is copied, it's author will be selected
        """
        title = f'Mass unban by {ctx.author}'
        unbanned = [u async for u in self._execute_users(ctx, users,
                                                         action='unban',
                                                         reason=title,
                                                         success_word='unbanned')]
        await self._display_mass(ctx, title, unbanned)
        
    async def _execute_users(self, ctx, users, *, action: str, reason: Union[str, None], success_word: str):
        for user in sorted(filter(None, tuple(set(users))), key=str):
            try:
                await eval(f"ctx.guild.{action}(user, reason=reason)")
            except DiscordException as e:
                yield str(user), str(e)
            else:
                yield str(user), f'Successfully {success_word}'
                
    def _format_events(self, ctx, event_type: str, user_and_action: Tuple[str, str]):
        for chunk in chunker(user_and_action):
            embed = ColoredEmbed(title=event_type)
            for name, value in chunk:
                embed.add_field(name=name, value=value, inline=False)
            yield embed
            
    async def _display_mass(self, ctx, title, container):
        await ctx.display(embeds=[*self._format_events(ctx, title, container)] 
                          or ColoredEmbed(title=f"Couldn't find anyone to {title.split()[1]}"))
    
    
def setup(bot):
    bot.add_cog(MemberModerationCog(bot))