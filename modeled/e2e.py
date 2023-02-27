''' Returns both the design and category of a given part.'''
# pylint: disable=R0903

import os
import json

import cv2
import numpy as np
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.ERROR)


# ---------------------------------------------------------------------------- #
#                             Directories and Paths                            #
# ---------------------------------------------------------------------------- #
MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')


class PartInference:
    ''' Returns both the design and category of a given part.'''

    def __init__(self):
        # -------------------------------- Load Model -------------------------------- #
        # Get system info
        with open('/opt/OpenBlok/system.json', 'r', encoding="UTF-8") as system_file:
            system_info = json.load(system_file)
        model_version = system_info['models']['e2e']['version']

        self.model = tf.keras.models.load_model(
            os.path.join(MODELS, f'e2e_{model_version}.h5'), compile=False)

        properties_file_location = os.path.join(
            MODELS, f'e2e_{model_version}.json')
        with open(properties_file_location, encoding="UTF-8") as properties_file:
            self.model_properties = json.load(properties_file)

    def get_predictions(self, raw):
        '''
        Uses the AI model to predict the part.
        '''
        designs = self.model_properties['designs']
        categories = self.model_properties['categories']

        # ----------------------------- Process Raw Frame ---------------------------- #
        raw = cv2.resize(
            raw,
            (self.model_properties['image_width'],
             self.model_properties['image_height']),
            interpolation=cv2.INTER_CUBIC
        )

        raw = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
        raw = tf.convert_to_tensor(raw, dtype=tf.float32)

        img_array = tf.keras.utils.img_to_array(raw)
        img_array = tf.expand_dims(img_array, 0)

        # ----------------------------- Make Predictions ----------------------------- #
        predictions = self.model.predict(img_array)

        design = designs[np.argmax(predictions[0])]
        design_confidence = 100 * np.max(predictions[0])

        category = categories[np.argmax(predictions[1])]
        category_confidence = 100 * np.max(predictions[1])

        print(f"Design #{design} | {design_confidence:.2f}%")
        print(f"Category {category} | {category_confidence:.2f}%")

        return {
            "design": [design, design_confidence],
            "category": [category, category_confidence]
        }
