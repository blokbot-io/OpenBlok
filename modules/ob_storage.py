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
            # print("WARNING | Local storage is disabled. Can't save image.")
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

    def clear_db(self):
        for key in self.redis.scan_iter("*"):
            self.redis.delete(key)

    def add_frame(self, queue_name, frame, metadata):
        '''
        Adds a frame to the redis queue
        '''
        frame_uuid = str(uuid.uuid4())

        frame_bytes = cv2.imencode(
            '.png', frame,
            [int(cv2.IMWRITE_PNG_COMPRESSION), 0]
        )[1].tostring()

        self.redis.hset(f"{queue_name}:{frame_uuid}", "frame", frame_bytes)

        for key, value in metadata.items():
            self.redis.hset(f"{queue_name}:{frame_uuid}", key, value)

        self.redis.rpush(queue_name, frame_uuid)

        return frame_uuid

    def get_frame(self, queue_name, delete_frame=True, frame_uuid=None):
        '''
        Gets a frame from the redis queue
        '''
        if frame_uuid is None:
            frame_uuid = self.redis.blpop([queue_name], timeout=30)[1].decode("utf-8")
        elif isinstance(frame_uuid, bytes):
            frame_uuid = frame_uuid.decode("utf-8")

        frame_bytes = self.redis.hget(f"{queue_name}:{frame_uuid}", "frame")
        frame_nparray = np.asarray(bytearray(frame_bytes), dtype="uint8")
        frame_decoded = cv2.imdecode(frame_nparray, cv2.IMREAD_COLOR)

        other_metadata = self.redis.hgetall(f"{queue_name}:{frame_uuid}")

        frame_object = {
            "uuid": frame_uuid,
            "frame": frame_decoded,
        }

        for key, value in other_metadata.items():
            key = key.decode("utf-8")
            if key not in ["frame"]:
                frame_object[key] = value.decode("utf-8")
                # frame_object[key] = json.loads(frame_object[key])

        if delete_frame:
            self.redis.delete(f"{queue_name}:{frame_uuid}")

        return frame_object

    def add_metadata(self, queue_name, frame_uuid, metadata):
        '''
        Adds metadata to a frame in the redis queue
        '''
        if isinstance(frame_uuid, bytes):
            frame_uuid = frame_uuid.decode("utf-8")

        for key, value in metadata.items():
            self.redis.hset(f"{queue_name}:{frame_uuid}", key, value)

    def move_frame(self, queue_name, new_queue_name, frame_uuid):
        '''
        Moves a frame from one queue to another
        '''
        self.redis.rename(f"{queue_name}:{frame_uuid}", f"{new_queue_name}:{frame_uuid}")
        self.redis.rpush(new_queue_name, frame_uuid)
