''' Returns both the design and category of a given part.'''

import os
import json

import cv2
import numpy as np
import tensorflow as tf

# ---------------------------------------------------------------------------- #
#                             Directories and Paths                            #
# ---------------------------------------------------------------------------- #
MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
E2E_MODEL = os.path.join(MODELS, 'e2e_model.h5')

# -------------------------------- Load Model -------------------------------- #
model = tf.keras.models.load_model(E2E_MODEL)
with open(os.path.join(MODELS, 'e2e_model.json')) as properties_file:
    model_properties = json.load(properties_file)

def get_predictions(raw):
    '''
    Uses the AI model to predict the part.
    '''
    designs = model_properties['designs']
    categories = model_properties['categories']

    # ----------------------------- Process Raw Frame ---------------------------- #
    raw = cv2.resize(
        raw,
        (model_properties['image_width'], model_properties['image_height']),
        interpolation=cv2.INTER_CUBIC
    )

    raw = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
    raw = tf.convert_to_tensor(raw, dtype=tf.float32)

    img_array = tf.keras.utils.img_to_array(raw)
    img_array = tf.expand_dims(img_array, 0)

    # ----------------------------- Make Predictions ----------------------------- #
    predictions = model.predict(img_array)

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
