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
from asyncio import FIRST_COMPLETED
from asyncio import wait as async_wait
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import sleep as async_sleep
from typing import List, Union, Tuple, Dict

from discord.ext.commands import EmojiConverter, BadArgument
from discord import RawReactionActionEvent, Embed, HTTPException, Message

class MioDisplay:
    def __init__(self, **options):
        """
        Base class that defines some helper functions
        """        
        # General context
        self.ctx = options.pop('ctx', None)
        self.bot = options.pop('bot', None) or self.ctx.bot
        self.loop = options.pop('loop', None) or self.ctx.bot.loop
        self.channel = options.pop('channel', None) or self.ctx.channel
        self.is_running = True
        
        # Displayed stuff
        self.embed = options.pop('embed', None)
        self.content = options.pop('content', None)
        self.embeds = options.pop('embeds', []) or [self.embed]
        self.contents = options.pop('contents', []) or [self.content]
        
        # Wait for reaction / message            
        self.author_only = options.pop('author_only', True)
        self.timeout = options.pop('timeout', 30)
        self.cooldown = options.pop('cooldown', 3)

        # shouldn't be edited
        self._last_pressed = perf_counter() - self.cooldown
        self._unable_to_delete = False
        self._index = options.pop('index', 0)
        self._max_index = max(len(self.contents) - 1, len(self.embeds) - 1)    
        self._raw_buttons = {
            k: v for k, v in filter(None, map(lambda n: getattr(getattr(self, n), '_button', None), dir(self)))
        }   

    async def start(self):
        """Only sends the initial message and adds reactions"""          
        self._index, self._max_index, to_send = await self.__move_page(self._index)
        
        self.msg = await self.channel.send(**to_send)
        
        self._buttons = await self.__add_reactions(self._raw_buttons)

    async def run_until_complete(self):
        """Keeps cycling until a stop order is given

        Returns:
            self -- When the cycle is done.
        """        
        await self.start()

        while self.is_running:
            await self.cycle()

        await self.after()
        
        return self
    
    async def run_once(self):
        """Runs once"""
        for method in (self.start, self.cycle, self.after):
            await method()
            
        return self
    
    async def cycle(self) -> Union[RawReactionActionEvent, None]:
        """Cycles once

        Returns:
            RawReactionEvent -- The received payload, or None if the wait_for timed out
        """        
        payload, self._unable_to_delete = await self.wait_for_reaction(self._unable_to_delete)
        return await self.__dispatch(payload)
       
    async def after(self):
        """To override, automatically called when it stops"""
        await self.msg.delete()   
        await self.ctx.add_reaction('🍓') 

    async def clear_reactions(self):
        """
        Removes the reactions, clears it if possible, 
        otherwise removes them 1 by 1
        """
        try:
            await self.msg.clear_reactions()
        except HTTPException:
            msg = await self.msg.channel.fetch_message(self.msg.id)
            for reaction in msg.reactions:
                if reaction.me: 
                    self.loop.create_task(reaction.remove(self.bot.user))
            
    # Control displayed pages
    async def page_up(self, amount: int = 1):
        """Moves goes up a certain amount of pages"""
        self._index, self._max_index, to_send = await self.__move_page(self._index + amount)
        await self.msg.edit(**to_send)        

    async def page_down(self, amount: int = 1):
        """Moves down a certain amount of pages"""
        self._index, self._max_index, to_send = await self.__move_page(self._index - amount)
        await self.msg.edit(**to_send)

    async def goto_index(self, position: Union[int, str]):
        """Goes to the specified page"""
        if position == 'FIRST': 
            new_index = 0
        elif position == 'LAST': 
            new_index = self._max_index
        else: 
            new_index = position
        
        self._index, self._max_index, to_send = await self.__move_page(new_index)
        await self.msg.edit(**to_send)
        
    # lvl 3
    async def __move_page(self, new_amount: int) -> Tuple[int, int, Dict]:
        """
        Does all necessary checks, adds a footer to the embed if needed,
        also handles internal cooldown
        """
        self._index = self.__check_page_index(new_amount)

        max_index, to_send = self.__formatter(self._index)

        new = perf_counter()
        
        await async_sleep(self.cooldown - (new - self._last_pressed))
        self._last_pressed = new

        return self._index, max_index, to_send

    # lvl 2  
    def __formatter(self, index) -> Tuple[int, Dict]:
        """Formats the embed with the current page"""
        curr_content, curr_embed = [*self.__curr_pages(self.contents, self.embeds, index)]

        max_index = max(len(self.contents) - 1, len(self.embeds) - 1) 

        curr_embed = self.__format_embed(curr_embed, self._index, max_index)

        return max_index, {'content': curr_content, 'embed': curr_embed}

    async def __add_reactions(self, raw_buttons: dict) -> dict:
        """
        Tries to convert the emoji and adds it to the message 
        according to their index, raises TypeError if an emoji is 
        registered twice
        """
        buttons = {}

        for _, (emoji, func) in sorted(self._raw_buttons.items()):
            try:
                emoji_obj = await EmojiConverter().convert(self.ctx, emoji)
            except BadArgument:
                emoji_obj = emoji
            finally:
                self.bot.loop.create_task(self.msg.add_reaction(emoji_obj))  
                buttons = self.__update_buttons(buttons, emoji, func)
        return buttons

    async def wait_for_reaction(self, unable_to_delete: bool
                                ) -> Tuple[Union[RawReactionActionEvent, None], bool]:
        """
        Waits for a reaction add or a reaction remove depending on whether
        it could remove the reaction or not
        """
        def check(p : RawReactionActionEvent):
            return (p.message_id == self.msg.id 
                    and p.channel_id == getattr(self.msg.channel, 'id', None)
                    and (p.user_id == self.ctx.author.id 
                         or not self.author_only 
                         and p.user_id != self.bot.user.id))
        
        wf_kwargs = {'timeout': self.timeout, 
                     'check': check}
        
        to_wait_for = [self.bot.wait_for('raw_reaction_add', **wf_kwargs)]
        
        if unable_to_delete:
            to_wait_for.append(self.bot.wait_for('raw_reaction_remove', **wf_kwargs))

        done, pending = await async_wait(to_wait_for, return_when=FIRST_COMPLETED)
        
        try:
            payload = done.pop().result()

        except AsyncTimeoutError:
            to_return = None    
            self.is_running = False

        else:
            to_return = payload
            unable_to_delete = await self.__remove_reaction(payload)

        finally:
            [future.cancel() for future in pending]

        return to_return, unable_to_delete

    async def __dispatch(self, payload: Union[RawReactionActionEvent, None]
                         ) -> RawReactionActionEvent:
        """Tries to find the proper emoji"""
        try:
            await self._buttons[str(payload.emoji)](self, payload)
        except KeyError:
            pass
        finally:
            return payload
        
    async def wait_for_message(self) -> int:
        def check(m: Message):
            return (m.channel == self.msg.channel
                    and (m.author == self.ctx.author 
                         or not self.author_only 
                         and m.author != self.bot.user))
    
        while self.is_running:
            
            try:
                msg = await self.bot.wait_for('message', timeout=self.timeout, check=check)
                
            except AsyncTimeoutError:
                self.is_running = False
                return None
            
            else:
                self.loop.create_task(self.__delete_user_input(msg))
                return msg    
                        
    # lvl 1      
    def __check_page_index(self, index: int):
        """Checks if the index is a proper one"""
        if index > self._max_index:                        
            return self._max_index   
        
        elif index < 0:
            return 0
        
        else:
            return index

    def __curr_pages(self, contents: List[str], embeds: List[Embed], index: int
                     ) -> Tuple[Union[str, None], Union[Embed, None]]:
        """Returns the current pages or None if they don't exist"""
        for item in (contents, embeds):
            try:
                yield item[index]
            except IndexError:
                yield None

    def __format_embed(self, curr_embed: Union[Embed, None],
                       index: int, max_index: int) -> Embed:
        """Sets a footer for embeds"""
        if curr_embed is None:
            return None

        return curr_embed.set_footer(text=f"Page {index + 1} out of {max_index + 1}")

    def __update_buttons(self, curr_buttons: dict, emoji: str, func: callable) -> dict:
        if emoji in curr_buttons:
            raise TypeError(f"{emoji} is already registered as a button")
        else:
            curr_buttons[emoji] = func
            return curr_buttons

    async def __remove_reaction(self, payload: RawReactionActionEvent):
        if payload.event_type == 'REACTION_REMOVE':
            return False
        try:
            await self.msg.remove_reaction(payload.emoji, payload.member)
        except (HTTPException, AttributeError):
            return True
        else:
            return False
    
    async def __delete_user_input(self, msg: Message):
        channel = self.channel
        if channel.guild is None: 
            return
        try:
            await msg.delete()
        except HTTPException:
            pass
        
            
# helpers outside of the class
def button(*, emoji: str, position: int):
    def decorator(func):
        return DecoratorClass(emoji, position, func)
    return decorator


class DecoratorClass:
    def __init__(self, emoji, position, func):
        self._button = (position, (emoji, func))