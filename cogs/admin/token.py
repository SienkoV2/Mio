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
from base64 import b64decode

import cv2
import pytesseract

import discord
from discord.ext import commands

from config import WARN_LOG_CHANNEL
from utils.formatters import ColoredEmbed

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class WarnClient(discord.Client):
    def __init__(self, loop):
        super().__init__(loop=loop)
        self.text = ("**You or someone in your team leaked this bot's token !**\n"
                     'Please use https://discordapp.com/developers/applications/ '
                     'to reset it')
        
    async def on_ready(self):
        self.guild_len = len(self.guilds)
        appinfo = await self.application_info()
        self.owner = appinfo.owner

        try:
            await appinfo.owner.send(self.text)
        except discord.Forbidden:
            pass
        
        if appinfo.team:
            self.team = appinfo.team.members
            for member in appinfo.team.members:
                try:
                    await member.send(self.text)
                except discord.Forbidden:
                    pass
        
        await self.close()


class TokenReader(commands.Cog, name='Admin'):
    def __init__(self, bot):
        self.bot = bot
        self.regex = r'([a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84})'
    
    @commands.Cog.listener('on_message')
    async def text_messages_listener(self, msg: discord.Message):
        if not (tokens:= findall(self.regex, msg.content)):
            return
        
        for token in tokens:  # unlikely to happen but w.e
            client = WarnClient(loop=self.bot.loop)
            try:
                await client.start(token)
            except Exception as e:
                embed = ColoredEmbed(title=f'Successfully sniped a token and logged in',
                                     description=e)
            else:
                embed = ColoredEmbed(title=f"Successfully sniped a token but couldn't log in ")
            finally:
                user_id = int(b64decode(token.split('.')[0]))
                user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                team = getattr(client, 'team', None) 
                if team:
                    team = ''.join([str(m) for m in team])
                
                fields = [('Message author', f'{msg.author} ({msg.author.id})', False),
                          ('Bot owner', f"{getattr(client, 'owner', None)}", False),
                          ('Team', team, False),
                          
                          ('Bot', f'{user} ({user.id})', False),
                          ('Bot account ?', user.bot, True),
                          ('Guild amount', getattr(client, 'guild_len', None), False),
                          
                          ('Guild', msg.guild.name, True),
                          ('Channel', msg.channel.mention, True),
                          ('Jump link', f'[Jump url]({msg.jump_url})', True)]                     

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                
                await self.bot.get_channel(WARN_LOG_CHANNEL).send(embed=embed)    
    
    @commands.Cog.listener('on_message')
    async def images_listener(self, msg: discord.Message):
        if msg.embeds:
            return
        
        for embed in msg.embeds:
            if embed.type != 'image':
                continue
            
            bytes_img = await 
            
        
        
        
    
    
    def extract_from_img(self, filename: str):
        img = cv2.imread(filename)
        return pytesseract.image_to_string(image=img)
        
    @commands.command(name='test')
    @commands.is_owner()
    async def test(self, ctx, filename: str):
        text = await self.bot.loop.run_in_executor(None, 
                                                   self.extract_from_img, 
                                                   filename)
        
        await ctx.send(text)
        
        

                        
                        
def setup(bot):
    bot.add_cog(TokenReader(bot))