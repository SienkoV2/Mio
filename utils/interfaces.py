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
from typing import Union

from discord import Embed, Message

from utils.miodisplay import MioDisplay, button

# Paginator - 10 pages or more 
class Paginator(MioDisplay):
    """Used to show multiple pages"""
    @button(emoji='🔢', position=0)
    async def on_input_emoji(self, payload):
        msg = await self.channel.send('Which page do you want to see ?')
        new_index = await self.wait_for_message()
        await self.goto_index(new_index - 1)
        await msg.delete()
            
    @button(emoji='⏮', position=1)
    async def on_full_back(self, payload): await self.goto_index('first')
    @button(emoji='◀', position=2)
    async def on_back(self, payload): await self.page_down()
    @button(emoji='▶', position=3)
    async def on_next_button(self, payload): await self.page_up()
    @button(emoji='⏭', position=4)
    async def on_full_forward(self, payload): await self.goto_index('last')
    @button(emoji='⏹', position=5)
    async def on_stop(self, payload): self.is_running = False
        
# Shortpaginator (2 - 5) pages
class ShortPaginator(MioDisplay):
    def __init__(self, ctx, **options):
        super().__init__(ctx, **options)
        self.buttons = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣')
            
    async def run_until_complete(self):
        await self.start()
        for emoji, _ in zip(self.buttons, range(self.max_index + 1)):
            await self.msg.add_reaction(emoji)
        await self.msg.add_reaction('⏹️')
        
        while self.is_running:
            payload, self.unable_to_delete = await self.wait_for_reaction(self.unable_to_delete)
            if (emoji := getattr(payload, 'emoji', None)):
                if str(emoji) == '⏹️':
                    self.is_running = False
                else:
                    await self.goto_index(self.buttons.index(str(emoji)))
                
        await self.after()
        
# Prompt - 1 page 
class Prompt(MioDisplay):
    """Used to display a single page"""
    @button(emoji='⏹', position=0)
    async def on_stop_button(self, payload): self.is_running = False
        
# Autodetection 
async def autodetect(ctx, **options) -> Union[Prompt, Paginator]:
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
        
    if max_len <= 1:
        return Prompt(ctx, contents=contents, embeds=embeds, **options)
    
    elif max_len <= 5:
        return ShortPaginator(ctx, contents=contents, embeds=embeds, **options)
    
    else:
        return Paginator(ctx, contents=contents, embeds=embeds, **options)    