'''
OpenBlok | ob_system.py
Responsible for the management and interaction of the system.json file
'''

import json

SYSTEM_FILE = '/opt/OpenBlok/system.json'


def get(key_path, default=None):
    '''
    Get a value from the system.json file
    '''
    return_value = default

    try:
        with open(SYSTEM_FILE, 'r', encoding="UTF-8") as system_file:
            system_info = json.load(system_file)

            if isinstance(key_path, list):
                for key in key_path:
                    system_info = system_info[key]
                return_value = system_info
            else:
                return_value = system_info[key_path]

    except (FileNotFoundError, KeyError) as error:
        print(error)

    return return_value
