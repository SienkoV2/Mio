from discord import Activity, ActivityType
from discord.ext.commands import when_mentioned_or

from config import DISCORD_TOKEN
from core import MioBot

params = {
    'command_prefix' : when_mentioned_or('yui '),
    'activity' : Activity(name='Fuwa Fuwa Time', 
                          type=ActivityType.listening)
}

if __name__ == '__main__':
    MioBot(**params).run(DISCORD_TOKEN)
    