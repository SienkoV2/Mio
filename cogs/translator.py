import discord
from discord.ext import commands

from aiogoogletrans import Translator, LANGUAGES, LANGCODES
from utils.converters import to_lower

class Translate(commands.Cog):
    def __init__(self, mio):
        self.mio = mio
        self.translator = Translator()

    @commands.group(name='translate', invoke_without_command=True)
    async def translate(self, ctx):
        """Translation commands"""
        await ctx.send_help(ctx.command)
        
        
    @translate.command(name='from')
    async def translate_from(self, ctx, *, text):
        """Translates a text to english"""        
        resp = await self.translator.translate(text)
        await self.__display(ctx, resp, text)

    @translate.command(name='to')
    async def translate_to(self, ctx, language : to_lower, *, text):
        """Translates a text to another language"""
        if (low := language) in LANGUAGES:
            lang = language
        else:
            lang = LANGCODES.get(language)
        if lang is None:
            raise LanguageNotFoundError(message=f"Couldn't find the language : {language}")
        
        resp = await self.translator.translate(text, dest=lang)
        
        await self.__display(ctx, resp, text)
        
    async def __display(self, ctx, resp, text) -> None:
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
        
        embed = discord.Embed(title="Translated something !", color=self.mio.color)
        
        fields = [('original', text, False), 
                  ('Translation', resp.text, False), 
                  ('Confidence', f_confidence, True),
                  ('Languages', f'{src} -> {dest}', True)]
        
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        
        await ctx.display(embed=embed)
    

    

class LanguageNotFoundError(commands.CommandError):
    pass




        
def setup(mio):
    mio.add_cog(Translate(mio))