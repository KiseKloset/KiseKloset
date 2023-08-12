import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class MediapipeSegmentation:
    def __init__(self, model_path):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.ImageSegmenterOptions(base_options=base_options)
        self.segmenter = vision.ImageSegmenter.create_from_options(options)

    def predict(self, frame: np.ndarray, threshold: float = 0.5):
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        segmentation_result = self.segmenter.segment(image)
        mask = segmentation_result.confidence_masks[0].numpy_view()
        mask = np.expand_dims(mask, -1) > threshold
        return mask
