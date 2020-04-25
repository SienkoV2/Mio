from re import findall
from asyncio import FIRST_COMPLETED
from asyncio import wait as async_wait
from asyncio import TimeoutError as AsyncTimeoutError
from typing import List, Any, Iterator, Iterable, Union, Tuple, Dict

from discord.ext.commands import EmojiConverter, BadArgument
from discord import RawReactionActionEvent, Embed, HTTPException, Message

class MioDisplay:
    def __init__(self, ctx, **options):
        """
        Base class that defines some helper functions, 
        not meant to be inherited from
        """
        # Easily accessible
        self.ctx = ctx
        self.mio = ctx.bot
        
        # Editable
        self.embeds = options.pop('embeds', [])
        self.contents = options.pop('contents', [])
        
        # Shouldn't be edited, but still accessible 
        self._channel = options.pop('channel', None) or ctx.channel
        self._timeout = options.pop('timeout', 30)
        self._author_only = options.pop('author_only', True)

        # checking that no options are left
        if options:
            f_options = '\n'.join(map(lambda kv: f"{kv[0]} : ({kv[1]})", options.items()))
            raise TypeError(f"Improper args :\n {f_options}")

        # do not touch 
        self.__index = options.pop('index', 0)
        self.__max_index = max(len(self.contents)-1, len(self.embeds)-1)    
        self.__unable_to_delete = False
        self.__is_closed = False
        self.__raw_buttons = {
            k : v for k, v in filter(None, map(lambda n: getattr(getattr(self, n), '_button', None), dir(self)))
        }   

    async def start(self):
        """Only sends the initial message"""          
        self.__index, self.__max_index, to_send = await self.__move_page(self.__index)
        self.msg = await self._channel.send(**to_send)
        self.__buttons = await self.__add_reactions(self.__raw_buttons)

    async def run_until_complete(self) -> True:
        """Keeps cycling until a stop order is given

        Returns:
            True -- When the cycle is done.
        """        
        await self.start()

        while not self.__is_closed:
            payload = await self.cycle()

        await self.after()
        return True
    
    async def cycle(self) -> Union[RawReactionActionEvent, None]:
        """Cycles once

        Returns:
            RawReactionEvent -- The received payload, or None if the wait_for timed out
        """        
        payload, self.__unable_to_delete = await self.__wait_for_reaction(self.__unable_to_delete)
        return await self.__dispatch(payload)
       
    # Control the session as a whole
    async def stop(self):
        """Stops cycling, changes the state of is_closed"""           
        self.__is_closed = True

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
                    await reaction.remove(self.mio.user)

    # get input from users (meant to be used by subclasses)
    async def wait_for_reaction(self):
        """
        Waits for a valid button to be pressed, calls the stop function in
        case of timeout
        """
        return await self.__wait_for_reaction(self.__unable_to_delete)

    async def wait_for_message(self):
        """
        Waits for a message containing a number
        calls the stop function in case of timeout
        """
        
        return await self.__wait_for_message()
        
    # Control displayed pages
    async def page_up(self, amount : int = 1):
        """Moves goes up a certain amount of pages"""
        self.__index, self.__max_index, to_send = await self.__move_page(self.__index + amount)
        await self.msg.edit(**to_send)        

    async def page_down(self, amount : int = 1):
        """Moves down a certain amount of pages"""
        self.__index, self.__max_index, to_send = await self.__move_page(self.__index 
                                                                       - amount)
        await self.msg.edit(**to_send)

    async def goto_index(self, position : Union[int, str]):
        """Goes to the specified page"""
        if position == 'first':
            new_index = 0
        
        elif position == 'last':
            new_index = self.__max_index

        else:
            new_index = position

        self.__index, self.__max_index, to_send = await self.__move_page(new_index)
        await self.msg.edit(**to_send)
    # lvl 3
    async def __move_page(self, new_amount : int) -> Tuple[int, int, Dict]:
        self.__index = await self.__check_page_index(new_amount)

        max_index, to_send = await self.__formatter(self.__index)

        return self.__index, max_index, to_send

    # lvl 2  
    async def __formatter(self, index) -> Tuple[int, Dict]:
        """Formats the embed with the current page"""
        curr_content, curr_embed = await self.__curr_pages(self.contents, 
                                                           self.embeds, 
                                                           index)

        max_index = max(len(self.contents)-1, len(self.embeds)-1) 

        curr_embed = await self.__format_embed(curr_embed, 
                                               self.__index, 
                                               max_index)

        return max_index, {'content' : curr_content, 'embed' : curr_embed}

    async def __add_reactions(self, raw_buttons : dict) -> dict:
        """
        Tries to convert the emoji and adds it to the message 
        according to their index, raises TypeError if an emoji is 
        registered twice
        """
        buttons = {}

        for _, (emoji, func) in sorted(self.__raw_buttons.items()):
            try:
                emoji_obj = await EmojiConverter().convert(self.ctx, emoji)

            except BadArgument:
                emoji_obj = emoji

            finally:
                await self.msg.add_reaction(emoji_obj)  
                buttons = await self.__update_buttons(buttons, emoji, func)

        return buttons

    async def __wait_for_reaction(self, 
                                  unable_to_delete : bool
                                  ) -> Tuple[Union[RawReactionActionEvent, None], bool]:
        """
        Waits for a reaction add or a reaction remove depending on whether
        it could remove the reaction or not
        """
        def check(p : RawReactionActionEvent):
            return (p.message_id == self.msg.id 
                    and p.channel_id == self.msg.channel.id
                    and (p.user_id == self.ctx.author.id 
                         or not self._author_only 
                         and p.user_id != self.bot.user.id))
        
        to_wait_for = [self.mio.wait_for('raw_reaction_add', 
                                         timeout=self._timeout, 
                                         check=check)]
        if unable_to_delete:
            to_wait_for.append(self.mio.wait_for('raw_reaction_remove', 
                                                 timeout=self._timeout, 
                                                 check=check))

        done, pending = await async_wait(to_wait_for, return_when=FIRST_COMPLETED)
        
        try:
            payload = done.pop().result()

        except AsyncTimeoutError:
            to_return = None    
            await self.stop()

        else:
            to_return = payload
            unable_to_delete = await self.__remove_reaction(payload)

        finally:
            [future.cancel() for future in pending]

        return to_return, unable_to_delete

    async def __dispatch(self, 
                         payload : Union[RawReactionActionEvent, None]
                        ) -> RawReactionActionEvent:
        """Tries to find the proper emoji"""
        try:
            await self.__buttons[str(payload.emoji)](self, payload)

        except KeyError:
            pass

        finally:
            return payload
        
    async def __wait_for_message(self) -> int:
        def check(m : Message):
            return (m.channel == self.msg.channel
                    and (m.author == self.ctx.author 
                         or not self._author_only 
                         and m.author != self.bot.user))
    
        while True:
            try:
                msg = await self.mio.wait_for('message', timeout=self._timeout, check=check)
            
            except AsyncTimeoutError:
                await self.stop()
                return None
            
            else:
                if (new_index := findall(r"(\d+)", msg.content)):
                    await self.__delete_user_input(msg)
                    return int(new_index[0])    

    # lvl 1      
    async def __check_page_index(self, index : int):
        """Checks if the index is a proper one"""
        if index > self.__max_index:                        
            return self.__max_index   
        
        elif index < 0:
            return 0

        else:
            return index

    async def __curr_pages(self, 
                           contents : List[str], 
                           embeds : List[Embed], 
                           index : int
                          ) -> Tuple[Union[str, None], Union[Embed, None]]:
        """Returns the current pages or None if they don't exist"""
        to_return = []
        for item in (contents, embeds):
            try:
                to_return.append(item[index])
            except IndexError:
                to_return.append(None)

        return to_return

    async def __format_embed(self,
                             curr_embed : Union[Embed, None],
                             index : int,
                             max_index : int,
                            ) -> Embed:
        """Sets a footer for embeds"""
        if curr_embed is None:
            return None

        return curr_embed.set_footer(text = f"Page {index + 1} out of {max_index + 1}")

    async def __update_buttons(self, curr_buttons : dict, emoji : str, func : callable) -> dict:
        if emoji in curr_buttons.keys():
            raise TypeError(f"{emoji} is already registered as a button")
        
        else:
            curr_buttons[emoji] = func
            return curr_buttons

    async def __remove_reaction(self, payload : RawReactionActionEvent):
        if payload.event_type  == 'REACTION_REMOVE':
            return False

        try:
            await self.msg.remove_reaction(payload.emoji, payload.member)

        except (HTTPException, AttributeError):
            return True

        else:
            return False
    
    async def __delete_user_input(self, msg : Message):
        try:
            await msg.delete()
        except HTTPException:
            pass
        
# helpers outside of the class
def button(*, emoji : str, position : int):
    def decorator(func):
        return DecoratorClass(emoji, position, func)
    return decorator

class DecoratorClass:
    def __init__(self, emoji, position, func):
        self._button = (position, (emoji, func))

