'''
Interacts with the location model to get the location of the object in the frame.
'''
# pylint: disable=R0903

import os
import json

import cv2
import tensorflow as tf


# ---------------------------------------------------------------------------- #
#                             Directories and Paths                            #
# ---------------------------------------------------------------------------- #
MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')


class LocationInference:
    ''' Interacts with the location model to get the location of the object in the frame. '''

    def __init__(self):
        # -------------------------------- Load Model -------------------------------- #
        # Get system info
        with open('/opt/OpenBlok/system.json', 'r', encoding="UTF-8") as system_file:
            system_info = json.load(system_file)
        model_version = system_info['models']['location']['version']

        self.model = tf.keras.models.load_model(
            os.path.join(MODELS, f'location_{model_version}.h5'), compile=False)

        properties_file_location = os.path.join(
            MODELS, f'location_{model_version}.json')
        with open(properties_file_location, encoding="UTF-8") as properties_file:
            self.model_properties = json.load(properties_file)

    def get_location(self, frame):
        '''
        Get the location of the object in the frame.
        Returns the x,y coordinates for the side and top views.
        '''
        frame_resized = cv2.resize(
            frame,
            (self.model_properties['input_width'],
             self.model_properties['input_height']),
            interpolation=cv2.INTER_CUBIC
        )

        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        frame_tensor = tf.convert_to_tensor(frame_rgb, dtype=tf.float32)
        frame_batch = tf.expand_dims(frame_tensor, 0)

        predictions = self.model.predict(frame_batch)
        _, side, top = predictions

        side_x = int(side[0][0] * frame.shape[1])
        side_y = int(side[0][1] * frame.shape[0])

        top_x = int(top[0][0] * frame.shape[1])
        top_y = int(top[0][1] * frame.shape[0])

        return {
            "sideMidpoint": [side_x, side_y],
            "topMidpoint": [top_x, top_y]
        }
