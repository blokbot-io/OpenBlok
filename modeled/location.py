''' Interacts with the location model to get the location of the object in the frame. '''

import os
import json

import cv2

import tensorflow as tf


# ---------------------------------------------------------------------------- #
#                             Directories and Paths                            #
# ---------------------------------------------------------------------------- #
MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
LOCATION_MODEL = os.path.join(MODELS, 'location_model.h5')

# -------------------------------- Load Model -------------------------------- #
model = tf.keras.models.load_model(LOCATION_MODEL)
with open(os.path.join(MODELS, 'location_model.json')) as properties_file:
    model_properties = json.load(properties_file)

def get_location(frame):
    '''
    Get the location of the object in the frame.
    Returns the x,y coordinates for the side and top views.
    '''
    frame_shape = frame.shape

    frame_resized = cv2.resize(
        frame,
        (model_properties['input_width'], model_properties['input_height']),
        interpolation = cv2.INTER_CUBIC
    )

    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    frame_tensor = tf.convert_to_tensor(frame_rgb, dtype=tf.float32)
    frame_batch = tf.expand_dims(frame_tensor, 0)

    predictions = model.predict(frame_batch)
    side, top = predictions

    side_x = int(side[0][0] * frame_shape[1])
    side_y = int(side[0][1] * frame_shape[0])

    top_x = int(top[0][0] * frame_shape[1])
    top_y = int(top[0][1] * frame_shape[0])

    return (side_x, side_y), (top_x, top_y)
