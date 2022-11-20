''' bloks | updater.py '''

import re
import json
import requests

import xmltodict


def update_models():
    '''
    Checks if new model weights are available and downloads them if so.
    '''
    # Get system info
    with open('/opt/OpenBlok/system.json', 'r', encoding="UTF-8") as system_file:
        system_info = json.load(system_file)

    model_repository = 'https://cdn.blokbot.io'

    available_models = requests.get(model_repository)

    available_models = xmltodict.parse(available_models.text)
    available_models = available_models['ListBucketResult']['Contents']

    location_models = []
    for model in available_models:
        model_version = re.search(
            r'(?:models\/location\/location_)(\d*)(?:\.h5)', model['Key'])
        if model_version:
            location_models.append(int(model_version.group(1)))

    location_models = location_models.sort(reverse=True)

    if location_models and location_models[0] > system_info['models']['location']['version']:
        print('INFO | Downloading new location model...')

        # Download new model weights
        location_model_h5 = requests.get(
            f'{model_repository}/models/location/location_{location_models[0]}.h5')
        with open('/opt/OpenBlok/modeled/models/location.h5', 'wb') as model_file:
            model_file.write(location_model_h5.content)

        # Download new model json
        location_model_json = requests.get(
            f'{model_repository}/models/location/location_{location_models[0]}.json')
        with open('/opt/OpenBlok/modeled/models/location_{location_models[0]}.json', 'wb') as model_file:
            model_file.write(location_model_json.content)
