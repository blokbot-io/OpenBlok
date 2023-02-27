'''
OpenBlok | sub_processes | ob_predictions.py

Performs predictions on the frames in the queue.
'''

import time

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
        time_start_get_frame = time.time()
        roi_frame_object = redis_db.get_frame("roi")
        time_get_frame = time.time() - time_start_get_frame

        roi_frame = roi_frame_object['frame']
        predicted_metadata = roi_frame_object['metadata']

        # Run location model
        time_start_location = time.time()
        part_location = location_model.get_location(roi_frame)
        time_location = time.time() - time_start_location

        side_midpoint = part_location['sideMidpoint']
        top_midpoint = part_location['topMidpoint']

        predicted_metadata['roi']['inferences'] = {"location": {}}

        predicted_metadata['roi']['inferences']['location']['sideMidpoint'] = side_midpoint
        predicted_metadata['roi']['inferences']['location']['topMidpoint'] = top_midpoint

        if [0, 0] not in [side_midpoint, top_midpoint] and top_midpoint[0] > roi_frame.shape[1]//3:
            top_midpoint[0] = top_midpoint[0] - roi_frame.shape[1]//3

            side_crop = crop_square(
                roi_frame[:, :roi_frame.shape[1]//3],
                (side_midpoint[0], side_midpoint[1])
            )

            top_crop = crop_square(
                roi_frame[:, roi_frame.shape[1]//3:],
                (top_midpoint[0], top_midpoint[1])
            )

            view_concatenated = np.concatenate(
                (side_crop['croppedFrame'], top_crop['croppedFrame']), axis=1)

            # Run e2e model
            predictions = e2e_model.get_predictions(view_concatenated)

            predicted_metadata['roi']['inferences']['location']['crop'] = {}
            predicted_metadata['roi']['inferences']['location']['crop']['topView'] = {}
            predicted_metadata['roi']['inferences']['location']['crop']['sideView'] = {}
            predicted_metadata['roi']['inferences']['e2e'] = {}

            predicted_metadata['roi']['inferences']['location']['crop']['topView']['upperLeft'] = top_crop['topLeftCoordinate']
            predicted_metadata['roi']['inferences']['location']['crop']['topView']['lowerRight'] = top_crop['bottomRightCoordinate']

            predicted_metadata['roi']['inferences']['location']['crop']['sideView']['upperLeft'] = side_crop['topLeftCoordinate']
            predicted_metadata['roi']['inferences']['location']['crop']['sideView']['lowerRight'] = side_crop['bottomRightCoordinate']

            predicted_metadata['roi']['inferences']['e2e']['design'] = predictions['design']
            predicted_metadata['roi']['inferences']['e2e']['category'] = predictions['category']

        # rotated_frame_object = redis_db.get_frame(
        #     "rotated", frame_uuid=predicted_metadata['rotatedUUID'])

        predicted_metadata['benchmarking']['prediction'] = {}
        predicted_metadata['benchmarking']['prediction']['timeGetFrame'] = time_get_frame
        predicted_metadata['benchmarking']['prediction']['timeLocation'] = time_location

        try:
            rotated_frame_object = redis_db.get_frame(
                "raw", frame_uuid=predicted_metadata['rawUUID'])

            redis_db.add_frame("predicted", rotated_frame_object['frame'], predicted_metadata)
        except Exception as e:
            print(e)
