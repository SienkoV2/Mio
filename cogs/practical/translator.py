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

from discord import Embed
from discord.ext.commands import Cog, group,CommandError

from aiogoogletrans import Translator, LANGUAGES, LANGCODES
from utils.converters import to_lower

def to_language(arg : str) -> Tuple[Union[str, None], str]:
    """Converts a string to a valid aiogoogletrans language

    Arguments:
        arg {str} -- the string to convert

    Returns:
        Tuple -- language if found else none + original
    """    
    lang = None
    if (low := arg) in LANGUAGES:
        lang = arg
    else:
        lang = LANGCODES.get(arg)
    return (lang, arg)

class TranslatorCog(Cog, name='Practical'):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

    @group(name='translate', invoke_without_command=True)
    async def translate(self, ctx):
        """Translation commands"""
        await ctx.send_help(ctx.command)
        
    @translate.command(name='from')
    async def translate_from(self, ctx, language : to_language, *, text : str):
        """
        Translates a text from a language to english
        Will use the whole text if the language isn't provided
        """        
        lang, original = language
        if lang is None:
            text = original + text
        resp = await self.translator.translate(text, src=lang or 'auto')
        await self._display(ctx, resp, text)

    @translate.command(name='to')
    async def translate_to(self, ctx, language : to_language, *, text : str):
        """Translates a text to another language"""
        lang, original = language
        if lang is None:
            raise LanguageNotFoundError(message=f"Couldn't find the language : {language}")
        
        resp = await self.translator.translate(text, dest=language)
        
        await self._display(ctx, resp, text)
                
    async def _display(self, ctx, resp, text) -> None:
        """Displays the response 

        Arguments:
            ctx {commands.Context} -- ctx
            resp {Response} -- the translator's response
            text {str} -- The text that the user entered
        """        
        src = LANGUAGES.get(resp.src) or resp.src
        dest = LANGUAGES.get(resp.dest) or resp.dest
        
        if (r := round(resp.confidence * 100, 1)) < 50.0:
            f_confidence = f'{r}% (might be innacurate)'
        else:
            f_confidence = f'{r}%'
        
        embed = Embed(title="Translated something !", color=self.bot.color)
        
        fields = [('original', text, False), 
                  ('Translation', resp.text, False), 
                  ('Confidence', f_confidence, True),
                  ('Languages', f'{src} -> {dest}', True)]
        
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        
        await ctx.display(embed=embed)
                
class LanguageNotFoundError(CommandError):
    pass


    
        

        
def setup(bot):
    bot.add_cog(TranslatorCog(bot))
