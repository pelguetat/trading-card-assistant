import cv2
from ultralytics import YOLOWorld
import numpy as np
from inference.models import YOLOWorld
import supervision as sv

# Capture video from the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video stream")
else:

    model = YOLOWorld(model_id="yolo_world/l")
    classes = ["trading card"]
    model.set_classes(classes)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        # Rotate the frame if necessary

        results = model.infer(frame, confidence=0.1)
        detections = sv.Detections.from_inference(results)
        labels = [
            f"{classes[class_id]} {confidence:0.3f}"
            for class_id, confidence in zip(detections.class_id, detections.confidence)
        ]
        annotated_image = frame.copy()
        BOUNDING_BOX_ANNOTATOR = sv.BoundingBoxAnnotator(thickness=2)
        LABEL_ANNOTATOR = sv.LabelAnnotator(
            text_thickness=2, text_scale=1, text_color=sv.Color.BLACK
        )
        annotated_image = BOUNDING_BOX_ANNOTATOR.annotate(annotated_image, detections)
        annotated_image = LABEL_ANNOTATOR.annotate(
            annotated_image, detections, labels=labels
        )
        cv2.imshow("Video Stream", annotated_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
