import time
import cv2
import numpy as np
import supervision as sv

from tqdm import tqdm
from inference.models import YOLOWorld


model = YOLOWorld(model_id="yolo_world/l")
model.set_classes(["pokemon trading card"])


generator = sv.get_video_frames_generator(0)
# wait 5 seconds
time.sleep(5)

frame = next(iter(generator))
results = model.infer(frame, confidence=0.002)
detections = sv.Detections.from_inference(results).with_nms(threshold=0.1)
annotated_image = frame.copy()
BOUNDING_BOX_ANNOTATOR = sv.BoundingBoxAnnotator(thickness=2)
LABEL_ANNOTATOR = sv.LabelAnnotator(
    text_thickness=2, text_scale=1, text_color=sv.Color.BLACK
)
annotated_image = BOUNDING_BOX_ANNOTATOR.annotate(annotated_image, detections)
annotated_image = LABEL_ANNOTATOR.annotate(annotated_image, detections)
cv2.imshow("Video Stream", annotated_image)
