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


from discord.ext.commands import (BucketType, Cog, Cooldown, Group,
                                  MinimalHelpCommand)

from utils.formatters import ColoredEmbed, chunker


class MioHelpCommand(MinimalHelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'help': 'Shows help about the bot, a command or a category',
            'cooldown': Cooldown(1.0, 15, BucketType.member)})
        
    def get_command_signature(self, command):
        return '{0.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)
        
    async def send_bot_help(self, mapping):
        await self.context.display(embeds=[e async for e in self._format_bot_help(mapping)],
                                   channel=self.get_destination())

    async def send_cog_help(self, cog):
        filtered_commands = await self.filter_commands(cog.get_commands(), sort=True)
        if not filtered_commands:
            return
        
        embeds = [e async for e in self._format_group_help(cog.qualified_name, filtered_commands)]
        await self.context.display(embeds=embeds, channel=self.get_destination())
        
    async def send_group_help(self, group):
        filtered_commands = await self.filter_commands(group.commands, sort=True)
        if not filtered_commands:
            return
        
        embeds = [e async for e in self._format_group_help(group.qualified_name, filtered_commands)]
        await self.context.display(embeds=embeds, channel=self.get_destination())
                    
    async def _format_group_help(self, title, filtered_commands):
        """Formats the help provided for cogs and groups"""        
        for chunk in chunker(filtered_commands):
            embed = ColoredEmbed(title=title)
            
            for command in chunk:
                embed.add_field(name=self.get_command_signature(command), 
                                value=command.short_doc, 
                                inline=False)

            yield embed

    async def _format_bot_help(self, mapping):
        """Formats the help provided when help is invoked on it's own"""
        
        bot_commands = [(cog, com) for cog, com in mapping.items() if cog and com]
        sorted_commands = sorted(bot_commands, key=lambda tup: tup[0].qualified_name)
        
        for chunk in chunker(sorted_commands):
            embed = ColoredEmbed(title=f"{self.context.bot.user}'s general help command")
            
            for cog, command_list in chunk:
                filtered_commands = await self.filter_commands(command_list, sort=True)
                
                command_names = []
                for c in filtered_commands:
                    if isinstance(c, Group):
                        command_names.append(f"`{c.name} [+{len(c.commands)}]`")
                    else:
                        command_names.append(f"`{c.name}`")
                
                if filtered_commands:
                    embed.add_field(name=cog.qualified_name, 
                                    value=' | '.join(command_names), 
                                    inline=False)
                
            yield embed
       
                
class HelpCommandCog(Cog, name='Infos'):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MioHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command
        
        
def setup(bot):
    bot.add_cog(HelpCommandCog(bot))
