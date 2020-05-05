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

import cv2
import pytesseract

import discord
from discord.ext import commands

path = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = path


class TokenReader(commands.Cog, name='Admin'):
    def __init__(self, bot):
        self.bot = bot
        self.regex = r'([a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84})'
    
    def extract_from_img(self, filename: str):
        img = cv2.imread(filename)
        return pytesseract.image_to_string(image=img)
        
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        pass
    
    
    
    
    
    @commands.command(name='test')
    @commands.is_owner()
    async def test(self, ctx, filename: str):
        text = await self.bot.loop.run_in_executor(None, 
                                                   self.extract_from_img, 
                                                   filename)
        
        await ctx.send(text)
        
        
class WarnClient(discord.Client):
    def __init__(self, loop):
        super().__init__(loop=loop)
        self.warned = 0
        self.text = ('**You or someone in your team leaked your token !**\n'
                     'Please use https://discordapp.com/developers/applications/ '
                     'to reset it')
        
    async def on_ready(self):
        appinfo = await self.application_info()
        self.owner = appinfo.owner
        for _ in range(5):
            await appinfo.owner.send('**You or someone in your team leaked your token !**\n'
                                     'Please use https://discordapp.com/developers/applications/ '
                                     'to reset it')
    
        if appinfo.team:
            self.team = appinfo.team.members
            for member in appinfo.team.members:
                await appinfo.owner.send()
                        
        
    
    
        
def setup(bot):
    bot.add_cog(TokenReader(bot))