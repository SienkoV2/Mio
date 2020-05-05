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

from time import perf_counter

from random import randint
from random import choice as rng_choice

from asyncio import sleep as async_sleep
from asyncio import TimeoutError as AsyncTimeoutError

from discord import Emoji, Message
from discord.ext.commands import command, Cog, max_concurrency, BucketType, CommandError

from utils.formatters import ColoredEmbed


class ReactionTimeCog(Cog, name='Games'):
    __slots__ = ('bot',)
    
    def __init__(self, bot):
        self.bot = bot
        
    @command(name='reaction_time')
    @max_concurrency(1.0, BucketType.channel)
    async def reaction_time(self, ctx, min_delay: int = 3, max_delay: int = 6, timeout: int = 15):
        """Sends an embed and adds a random reaction"""
        if min_delay > max_delay:
            raise InvalidDelay(message='The minimal delay must be smaller than the maximum one')
            
        if max_delay > 120:
            raise InvalidBound(message='The maximum delay cannot be longer than ')
            
        if timeout > 30:
            raise InvalidBound(message='The timeout cannot be longer than 30 seconds')
            
        emoji = rng_choice(self.bot.emojis)

        embed = ColoredEmbed(title='Be the first to react when the emoji appears !')

        fields = [('minimum delay', f'{min_delay} seconds'),
                  ('maximum delay', f'{max_delay} seconds'),
                  ('emoji', str(emoji))]

        for name, value in fields:
            embed.add_field(name=name, value=value)

        msg = await ctx.send(embed=embed)

        await async_sleep(randint(min_delay, max_delay))

        await msg.add_reaction(emoji)
        start = perf_counter()
        embed = await self._handle_reactions(msg, emoji, embed, start, timeout)
        await msg.edit(embed=embed)

    @command(name='find_reaction')
    @max_concurrency(1.0, BucketType.channel)
    async def find_reaction(self, ctx, min_message_index: int = 0, 
                            max_message_index: int = 10, timeout: int = 15):
        
        if min_message_index > max_message_index:
            raise InvalidBound(message='The minimal message amount must be smaller than the maximum one')
    
        if max_message_index > 100:
            raise InvalidBound(message='The maximum amount of message cannot be bigger than 100')
    
        if timeout > 120:
            raise InvalidBound('The timeout cannot be longer than 120 seconds')
    
        emoji = rng_choice(self.bot.emojis)
    
        embed = ColoredEmbed(title='Find the reaction !')
    
        fields = [('minimum message amount', f'{min_message_index} messages'),
                  ('maximum message amount', f'{max_message_index} messages'),
                  ('emoji', str(emoji))]

        for name, value in fields:
            embed.add_field(name=name, value=value)
    
        to_edit = await ctx.send(embed=embed)
            
        messages = await ctx.history(limit=max_message_index).flatten()
        msg = rng_choice(messages[min_message_index:max_message_index])
        await msg.add_reaction(emoji)
        start = perf_counter()
        
        embed = await self._handle_reactions(msg, emoji, embed, start, timeout)
        await to_edit.edit(embed=embed)
        
    async def _handle_reactions(self, msg: Message, emoji: Emoji,
                                embed: ColoredEmbed, start: int, timeout: int):
        def check(p):
            return (p.channel_id == msg.channel.id 
                    and p.message_id == msg.id
                    and not p.member.bot
                    and str(p.emoji) == str(emoji))
            
        try:
            p = await self.bot.wait_for('raw_reaction_add', timeout=timeout, check=check)
        except AsyncTimeoutError:
            embed.add_field(name='Result', value='No one reacted on time', inline=False)
        else:
            fields = [('Winner', p.member.mention),
                      ('Time', f'{round(perf_counter() - start, 2)} seconds'),
                      ('Message', f'[Jump url]({msg.jump_url})')]
            
            for name, value in fields:
                embed.add_field(name=name, value=value)
        finally:
            return embed


class InvalidDelay(CommandError):
    pass


class InvalidBound(CommandError):
    pass


def setup(bot):
    bot.add_cog(ReactionTimeCog(bot))
