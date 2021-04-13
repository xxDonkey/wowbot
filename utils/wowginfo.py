import requests

from utils import default

config = default.get('config.json')

bosses = {
    'wrathion-the-black-emperor': 1,
    'maut': 2,
    'the-prophet-skitra': 3,
    'dark-inquisitor-xanesh': 4,
    'the-hivemind': 5,
    'shadhar-the-insatiable': 6,
    'drestagath': 7,
    'ilgynoth-corruption-reborn': 8,
    'vexiona': 9,
    'ra-den-the-despoiled': 10,
    'carapace-of-nzoth': 11,
    'nzoth-the-corruptor': 12
}

def get_guild_info(region, realm, name, difficulty='mythic'):
    info = {}
    
    for boss in list(bosses.keys()):
        link = f'https://raider.io/api/v1/guilds/boss-kill?region={region}&realm={realm}&guild={name.replace(" ", "%20")}&raid={config.current_raid_tier}&boss={boss}&difficulty={difficulty}'
        r = requests.get(link)
        if r.status_code != 200: 
            print(f'Status code {r.status_code} when requesting from {link}')
            return None

        if r.json() == {}:
            info[boss] = None
        else:
            info[boss] = r.json()['kill']['defeatedAt']

    return info

def get_guild_roster(realm, name, region='us', namespace='profile-us', locale='en_US'):
    _id = get_access_token(config.wow_api_id, config.wow_api_secret)
    params = {'namespace': namespace, 'locale': locale, 'access_token': _id}

    link = f'https://{region}.api.blizzard.com/data/wow/guild/{realm}/{name}/roster'
    r = requests.get(link, params=params)
    if r.status_code != 200: 
        print(f'Status code {r.status_code} when requesting from {link}')
        return None

    roster = r.json()['members']
    names = []

    for player in roster:
        names.append(player['character']['name'])

    return names

def get_access_token(_id, secret, region='us'):
    data = {'grant_type': 'client_credentials'}
    response = requests.post(f'https://{region}.battle.net/oauth/token', data=data, auth=(_id, secret))
    return response.json()['access_token']