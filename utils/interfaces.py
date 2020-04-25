from re import findall
from typing import Union

from discord import Embed, Message

from utils.miodisplay import MioDisplay, button

# Paginator - 10 pages or more 
class Paginator(MioDisplay):
    """Used to show multiple pages"""
    @button(emoji='🔢', position=0)
    async def on_input_emoji(self, payload):
        new_index = await self.wait_for_message()
        await self.goto_index(new_index - 1)
            
    @button(emoji='⏮', position=1)
    async def on_full_back(self, payload):
        await self.goto_index('first')

    @button(emoji='◀', position=2)
    async def on_back(self, payload):
        await self.page_down()

    @button(emoji='⏹', position=3)
    async def on_stop(self, payload):
        await self.stop()

    @button(emoji='▶', position=4)
    async def on_next_button(self, payload):
        await self.page_up()

    @button(emoji='⏭', position=5)
    async def on_full_forward(self, payload):
        await self.goto_index('last')
        
# Prompt - 1 page 
class Prompt(MioDisplay):
    """Used to display a single page"""
    @button(emoji='⏹', position=0)
    async def on_stop_button(self, payload):
        await self.stop()
        
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
        
    if max(len(contents), len(embeds)) <= 1:
        return Prompt(ctx, contents=contents, embeds=embeds, **options)
    
    else:
        return Paginator(ctx, contents=contents, embeds=embeds, **options)    