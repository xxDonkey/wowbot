import os

from utils import default
from utils.data import Bot

config = default.get('config.json')

print('Logging in...')

bot = Bot(
    command_prefix  = config.prefix,
    command_attrs   = dict(hidden=True)
)

for file in os.listdir('cogs'):
    if file.endswith('.py'):
        name = file[:-3]
        bot.load_extension(f'cogs.{name}')

bot.run(config.token)

