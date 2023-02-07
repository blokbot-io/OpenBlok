'''
OpenBlok | ob_storage.py
Manages the storage of images both locally and on the cloud.
'''

import os
import uuid
import json
import time

import cv2
import redis
import numpy as np

from modules import ob_system


# ---------------------------------------------------------------------------- #
#                                 Local Storage                                #
# ---------------------------------------------------------------------------- #
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
            return

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


# ---------------------------------------------------------------------------- #
#                                     Redis                                    #
# ---------------------------------------------------------------------------- #
class RedisStorageManager():
    '''Manages the redis storage'''

    HOST = ob_system.get(['storage', 'redis', 'host'])
    PORT = ob_system.get(['storage', 'redis', 'port'])
    PASSWORD = ob_system.get(['storage', 'redis', 'password'])

    def __init__(self):
        self.redis = redis.Redis(host=self.HOST, port=self.PORT, password=self.PASSWORD)

        for key in self.redis.scan_iter("*"):
            self.redis.delete(key)

    def add_frame(self, frame, frame_timestamp, queue_name):
        '''
        Adds a frame to the redis queue
        '''
        frame_uuid = str(uuid.uuid4())

        frame_bytes = cv2.imencode(
            '.png', frame,
            [int(cv2.IMWRITE_PNG_COMPRESSION), 0]
        )[1].tostring()

        self.redis.hset(f"{queue_name}:{frame_uuid}", "frame", frame_bytes)
        self.redis.hset(f"{queue_name}:{frame_uuid}", "timestamp", frame_timestamp)

        self.redis.rpush(queue_name, frame_uuid)

    def get_frame(self, queue_name):
        '''
        Gets a frame from the redis queue
        '''
        frame_uuid = self.redis.blpop([queue_name], timeout=10)[1].decode("utf-8")

        frame_bytes = self.redis.hget(f"{queue_name}:{frame_uuid}", "frame")
        frame_nparray = np.asarray(bytearray(frame_bytes), dtype="uint8")
        frame_decoded = cv2.imdecode(frame_nparray, cv2.IMREAD_COLOR)

        frame_timestamp = self.redis.hget(f"{queue_name}:{frame_uuid}", "timestamp")

        frame_object = {
            "frame": frame_decoded,
            "timestamp": frame_timestamp.decode("utf-8")
        }

        self.redis.delete(f"{queue_name}:{frame_uuid}")

        return frame_object
