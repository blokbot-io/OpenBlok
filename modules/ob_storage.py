'''
OpenBlok | ob_storage.py
Manages the storage of images both locally and on the cloud.
'''

import os
import uuid

from modules import ob_system


class LocalStorageManager:
    '''Adds images to the local storage and manages the local storage.'''

    _instance = None

    def __new__(cls):
        '''
        Singleton pattern
        '''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        '''
        Initialize the local storage manager.
        '''
        if hasattr(self, 'current_size'):
            return
        self.current_size = 0
        self.session_id = str(uuid.uuid4())
        self.path = ob_system.get(['storage', 'local', 'path'])
        self.max_size = ob_system.get(['storage', 'local', 'maxSizeGB'])

        os.makedirs(self.path, exist_ok=True)
        os.makedirs(os.path.join(self.path, self.session_id), exist_ok=True)
        self.calculate_current_size()

    def calculate_current_size(self):
        '''
        Calculate the current size of the local storage
        '''
        for path, _, files in os.walk(self.path):
            for file in files:
                self.current_size += os.path.getsize(os.path.join(path, file))

    def add_image(self, image):
        '''
        Add an image to the local storage
        '''
        image_path = os.path.join(self.path, self.session_id, str(uuid.uuid4()) + '.jpg')
        image.save(image_path, 'JPEG')
        self.current_size += os.path.getsize(image_path)
