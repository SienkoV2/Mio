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

from utils.formatters import ColoredEmbed
from discord.ext.commands import command, Cog, max_concurrency, BucketType, CommandError


class ReactionTimeCog(Cog, name='Games'):
    def __init__(self, bot):
        self.bot = bot
        
    @command(name='reaction_time')
    @max_concurrency(1.0, BucketType.channel)
    async def reaction_time(self, ctx, min_delay: int = 3, max_delay: int = 6):
        """Sends an embed and adds a random reaction"""
        if min_delay > max_delay:
            raise InvalidDelay(message=f'The minimal delay must be smaller than the maximum one')
            
        emoji = rng_choice(self.bot.emojis)

        embed = ColoredEmbed(title='Reaction time game')

        fields = [('minimum delay', f'{min_delay} seconds'),
                  ('maximum delay', f'{max_delay} seconds'),
                  ('emoji', str(emoji))]

        for name, value in fields:
            embed.add_field(name=name, value=value)

        msg = await ctx.send(embed=embed)

        await async_sleep(randint(min_delay, max_delay))

        await msg.add_reaction(emoji)

        def check(p):
            return (p.channel_id == msg.channel.id 
                    and p.message_id == msg.id
                    and not p.member.bot)
        try:
            p = await self.bot.wait_for('raw_reaction_add', timeout=5, check=check)
        except AsyncTimeoutError:
            embed.add_field(name='Result', value='No one reacted on time', inline=False)
        else:
            embed.add_field(name='Result', value=f"{p.member.mention} won", inline=False)
        finally:
            await msg.edit(embed=embed)


class InvalidDelay(CommandError):
    pass


def setup(bot):
    bot.add_cog(ReactionTimeCog(bot))
