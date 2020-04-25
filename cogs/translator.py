import discord
from discord.ext import commands

from aiogoogletrans import Translator, LANGUAGES

class Translate(commands.Cog):
    def __init__(self, mio):
        self.mio = mio
        self.translator = Translator()

    @commands.group(name='translate', invoke_without_subcommand=True)
    async def translate(self, ctx, *, text):
        resp = await self.translator.translate(text)
        
        try:
            src = LANGUAGES[resp.src]
        except KeyError:
            src = resp.src
        
        if (r := round(resp.confidence * 100, 1)) < 50.0:
            f_confidence = f'{r}% (might be innacurate)'
        else:
            f_confidence = f'{r}%'
        
        await ctx.display(embed = discord.Embed(title="Translated something !",
                                                color=self.mio.color
                                                ).add_field(
                                                    name='Original',
                                                    value=text,
                                                    inline=False
                                                ).add_field(
                                                    name='Translation',
                                                    value=resp.text,
                                                    inline=False
                                                ).add_field(
                                                    name='Source',
                                                    value=src,
                                                ).add_field(
                                                    name='Confidence',
                                                    value=f_confidence))

    @translate.command(name='to')
    async def translate_to(self, ctx, lang, *, text):
        pass
    


        
def setup(mio):
    mio.add_cog(Translate(mio))