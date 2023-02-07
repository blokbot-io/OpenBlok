'''
OpenBlok | ob_storage.py
Manages the storage of images both locally and on the cloud.
'''

import os
import uuid
import json
import time

import cv2

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
        self.session_id = str(round(time.time()))
        self.path = ob_system.get(['storage', 'local', 'path'])
        self.max_size_gb = ob_system.get(['storage', 'local', 'maxSizeGB'])
        self.max_size_bytes = self.max_size_gb * 1024 * 1024 * 1024

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

    def add_image(self, frame, frame_name=uuid.uuid4()):
        '''
        Add an image to the local storage
        '''
        if not ob_system.get(['storage', 'local', 'enabled']):
            print("WARNING | Local storage is disabled. Can't save image.")

        if self.current_size < self.max_size_bytes:
            image_path = os.path.join(self.path, self.session_id, str(frame_name) + '.png')
            cv2.imwrite(image_path, frame)
            self.current_size += os.path.getsize(image_path)
        else:
            print("WARNING | Local storage is full. Can't save image.")

    def session_metadata(self, metadata):
        '''
        Store session metadata in a file
        '''
        metadata_path = os.path.join(self.path, self.session_id, 'metadata.json')
        with open(metadata_path, 'w', encoding="UTF-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=4)
