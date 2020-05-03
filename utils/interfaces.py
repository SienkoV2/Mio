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


from typing import Union

from discord import Embed, Message

from utils.miodisplay import MioDisplay, button


class Prompt(MioDisplay):
    """Used to display a single page"""
    @button(emoji='⏹', position=100)
    async def on_stop_button(self, payload): 
        """Stops running"""
        self.is_running = False


class Paginator(Prompt):  
    """
    6 pages or more
    """
    @button(emoji='🔢', position=0)
    async def on_input_emoji(self, payload):
        msg = await self.channel.send('Which page do you want to see ?')
        while self.is_running:
            received_msg = await self.wait_for_message()
            try:
                new_index = int(received_msg.content)
            except ValueError:
                pass
            else:
                break
        else:
            new_index = 1
            
        await self.goto_index(new_index - 1)
        await msg.delete()
            
    @button(emoji='⏮', position=1)
    async def on_full_back(self, payload): 
        """First page"""
        await self.goto_index('FIRST')
        
    @button(emoji='◀', position=2)
    async def on_back(self, payload): 
        """Page - 1"""
        await self.page_down()
        
    @button(emoji='▶', position=3)
    async def on_next_button(self, payload): 
        """Page + 1"""
        await self.page_up()
        
    @button(emoji='⏭', position=4)
    async def on_full_forward(self, payload): 
        """Last page"""
        await self.goto_index('LAST')
        

class ShortPaginator(MioDisplay):
    """
    From 1 to 5 pages
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.buttons = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣')
            
    async def run_until_complete(self):
        await self.start()
        for emoji, _ in zip(self.buttons, range(self._max_index + 1)):
            await self.msg.add_reaction(emoji)
        await self.msg.add_reaction('⏹️')
        
        while self.is_running:
            payload, self._unable_to_delete = await self.wait_for_reaction(self._unable_to_delete)
            if (emoji:= getattr(payload, 'emoji', None)):
                if str(emoji) == '⏹️':
                    self.is_running = False
                else:
                    await self.goto_index(self.buttons.index(str(emoji)))
                
        await self.after()
        
# Prompt - 1 page 

        
# Autodetection 
def autodetect(**options) -> Union[Prompt, ShortPaginator, Paginator]:
    """Autodetects whether to return a prompt or a paginator 

    Arguments:
        ctx {Context} -- commands.Context

    Raises:
        TypeError: If both (content and contents)  
                   or (embed and embeds) are defined
    Returns:
        Union[Prompt, Paginator] -- Prompt or Paginator
    """    
    contents_embeds = []
    for singular, plural in [('content', 'contents'), ('embed', 'embeds')]:
        get_sing = options.pop(singular, [])
        get_plural = options.pop(plural, [])
        
        if get_sing and get_plural:
            raise TypeError(f"Both {singular} and {plural} are defined")
        
        curr = get_sing or get_plural
        
        if not isinstance(curr, list):
            curr = [curr]
        
        contents_embeds.append(curr)
        
    contents, embeds = contents_embeds
        
    max_len = max(len(contents), len(embeds))
    
    # should prolly switch to a for loop
    kwargs = {'contents': contents, 'embeds': embeds}
    
    for max_size, Interface in [(1, Prompt), (5, ShortPaginator)]:
        if max_len <= max_size:
            return Interface(**kwargs, **options)
    else:
        return Paginator(**kwargs, **options)
