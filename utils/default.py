import json
import pytz
import math
import traceback as tb

from datetime import datetime
from collections import namedtuple
from discord.utils import find

def get_json(file):
    try:
        with open(file, encoding='utf8') as data:
            return json.load(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")

def load_guild_info():
        try:
            with open('database/guildinfo.json', encoding='utf8') as f:
                return json.load(f)
        except AttributeError:
            raise AttributeError("Unknown argument")
        except FileNotFoundError:
            raise FileNotFoundError("JSON file wasn't found")

def save_guild_info(new_info):
    with open('database/guildinfo.json', 'w') as f:
        json.dump(new_info, f, indent=4)

def load_savedchars():
    try:
        with open('database/savedchars.json', encoding='utf8') as f:
            return json.load(f)
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")

def save_savedchars(updated_list):
    with open('database/savedchars.json', 'w') as f:
        json.dump( updated_list, f, indent=4)

config = get("config.json")

def get_traceback(err, advanced: bool=True):
    trace = ''.join(tb.format_tb(err.__traceback__))
    error = ('```py\n{1}{0}: {2}\n```').format(type(err).__name__, trace, err)
    return error if advanced else f"{type(err).__name__}: {err}"

def get_timestamp():
    timezone = pytz.timezone(config.timezone)
    return timezone.localize(datetime.now())

def round_to_nearest(x, b=1):
    return int(b * round(float(x) / b))

def floor_to_nearest(x, b=1):
    return int(b * math.floor(float(x) / b))

async def get_emoji(client, emoji_name, space_before=True):
    emoji_banks = [g for g in client.guilds if g.name.startswith('EmojiBank')]

    for bank in emoji_banks:
        emojis = await bank.fetch_emojis()
        for emoji in emojis:
            if emoji.name == emoji_name:
                if space_before: return f' <:{emoji.name}:{emoji.id}>'
                else: return f'<:{emoji.name}:{emoji.id}> '

    return ''