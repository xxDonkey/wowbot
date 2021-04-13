import requests
import json

from utils import default

config = default.get('config.json')

def get_character_data(region, realm, name, get_mythic_plus_data=True, get_raid_progression_data=True, get_class_data=True):
    raiderio_link = f'https://raider.io/api/v1/characters/profile?region={region}&realm={realm}&name={name}&fields=mythic_plus_best_runs%3Aall%2Craid_progression%2Cmythic_plus_scores_by_season%3Acurrent'
    r = requests.get(raiderio_link)
    if r.status_code != 200: 
        print(f'Status code {r.status_code} when requesting from {raiderio_link}')
        return None

    info = r.json()
    data = {}

    if get_mythic_plus_data:
        data['mythic_plus_score'] = info['mythic_plus_scores_by_season'][0]['scores']['all']

    if get_raid_progression_data:
        data['raid_progression'] = info['raid_progression'][config.current_raid_tier]['summary']

    if get_class_data:
        data['class'] = info['class']
        types = dict(config.armor_types._asdict())
        data['armor_type'] = types[info['class'].replace(' ', '_')]

    return data

