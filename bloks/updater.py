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

    model_repo = 'https://cdn.blokbot.io'

    available_models = requests.get(model_repo, timeout=10)

    available_models = xmltodict.parse(available_models.text)
    available_models = available_models['ListBucketResult']['Contents']

    # Check if new models are available
    for model_type in ['location', 'e2e']:
        versions = []
        for model in available_models:

            model_version = None

            if model_type == 'location':
                model_version = re.search(
                    r'(?:models\/location\/location_)(\d*)(?:\.h5)', model['Key'])

            if model_type == 'e2e':
                model_version = re.search(
                    r'(?:models\/e2e\/e2e_)(\d*)(?:\.h5)', model['Key'])

            if model_version:
                versions.append(int(model_version.group(1)))

        if not versions:
            print(f'ERROR | No {model_type} models available.')
            return

        versions.sort(reverse=True)

        if versions[0] > int(system_info['models'][f'{model_type}']['version'] or 0):
            print(f'INFO | Downloading new {model_type} model...')
            models_folder = '/opt/OpenBlok/modeled/models'

            # Download new model weights
            model_h5 = requests.get(
                f'{model_repo}/models/{model_type}/{model_type}_{versions[0]}.h5', timeout=10)
            with open(f'{models_folder}/{model_type}_{versions[0]}.h5', 'wb') as model_file:
                model_file.write(model_h5.content)

            # Download new model json
            model_json = requests.get(
                f'{model_repo}/models/{model_type}/{model_type}_{versions[0]}.json', timeout=10)
            with open(f'{models_folder}/{model_type}_{versions[0]}.json', 'wb') as model_file:
                model_file.write(model_json.content)

            # Update system info
            system_info['models'][f'{model_type}']['version'] = versions[0]
            with open('/opt/OpenBlok/system.json', 'w', encoding="UTF-8") as system_file:
                json.dump(system_info, system_file)
