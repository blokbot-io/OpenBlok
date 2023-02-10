'''
OpenBlok | sub_processes | ob_predictions.py

Performs predictions on the frames in the queue.
'''

import numpy as np

from bloks.utils import crop_square
from modules import ob_storage

from modeled import location, e2e


redis_db = ob_storage.RedisStorageManager()


def run_models():
    '''
    runs models on frames in the queue, stores results in Redis
    '''
    location_model = location.LocationInference()
    e2e_model = e2e.PartInference()

    while True:
        roi_frame_object = redis_db.get_frame("roi")

        roi_frame = roi_frame_object['frame']
        predicted_metadata = roi_frame_object['metadata']

        # Run location model
        side, top = location_model.get_location(roi_frame)

        predicted_metadata['roi']['inferences'] = {"location": {}}

        predicted_metadata['roi']['inferences']['location']['side'] = [side[0], side[1]]
        predicted_metadata['roi']['inferences']['location']['top'] = [top[0], top[1]]

        if 0 not in [side[0], side[1], top[0], top[1]] and top[0] > roi_frame.shape[1]//3:
            top[0] = top[0] - roi_frame.shape[1]//3

            side_crop = crop_square(
                roi_frame[:, :roi_frame.shape[1]//3],
                (side[0], side[1])
            )

            top_crop = crop_square(
                roi_frame[:, roi_frame.shape[1]//3:],
                (top[0], top[1])
            )

            view_concatenated = np.concatenate(
                (side_crop['croppedFrame'], top_crop['croppedFrame']), axis=1)
            predictions = e2e_model.get_predictions(view_concatenated)

            predicted_metadata['roi']['inferences']['location']['crop'] = {}
            predicted_metadata['roi']['inferences']['location']['crop']['topView'] = {}
            predicted_metadata['roi']['inferences']['location']['crop']['sideView'] = {}
            predicted_metadata['roi']['inferences']['e2e'] = {}

            predicted_metadata['roi']['inferences']['location']['crop']['topView']['upperLeft'] = top_crop[1]
            predicted_metadata['roi']['inferences']['location']['crop']['topView']['lowerRight'] = top_crop[2]

            predicted_metadata['roi']['inferences']['location']['crop']['sideView']['upperLeft'] = side_crop[1]
            predicted_metadata['roi']['inferences']['location']['crop']['sideView']['lowerRight'] = side_crop[2]

            predicted_metadata['roi']['inferences']['e2e']['design'] = predictions['design']
            predicted_metadata['roi']['inferences']['e2e']['category'] = predictions['category']

        rotated_frame_object = redis_db.get_frame(
            "rotated", frame_uuid=predicted_metadata['rotatedUUID'])
        redis_db.add_frame("predicted", rotated_frame_object['frame'], predicted_metadata)
