import cv2
from inference.models.yolo_world import YOLOWorld
import os
import threading

import tkinter as tk
import logging
import supervision as sv

# set this env variable export OPENCV_LOG_LEVEL=ERROR  # or NONE to completely silence
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
# # Event to trigger cropping
crop_event = threading.Event()


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def find_frame_with_most_bboxes(data):
    max_bboxes = 0
    best_frame_data = None

    # Find the frame with the most bounding boxes
    for frame, classes, bboxes, frame_count in data:
        if bboxes.shape[0] > max_bboxes:
            max_bboxes = bboxes.shape[0]
            best_frame_data = (frame, bboxes, frame_count)

    return best_frame_data


def crop_and_save_images_from_frame(frame_data, output_dir):
    saved_images = []

    if frame_data:
        frame, bboxes, frame_count = frame_data
        for i, bbox in enumerate(bboxes):
            x, y, x2, y2 = map(int, bbox)  # Convert coordinates to integers
            cropped_image = frame[y:y2, x:x2]
            # Convert BGR to RGB
            cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
            image_path = os.path.join(output_dir, f"frame_{frame_count}_crop_{i}.jpg")
            cv2.imwrite(image_path, cropped_image)
            logging.info(f"Cropped image saved at: {image_path}")
            saved_images.append(image_path)

    return saved_images


def crop_and_save_images(data):
    output_dir = "/Users/pabloelgueta/Documents/trading-card-assistant/cropped_images"
    best_frame_data = find_frame_with_most_bboxes(data)
    return crop_and_save_images_from_frame(best_frame_data, output_dir)


def process_video(frame_queue, terminate_flag):

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream")
        return

    # Reduce resolution for faster processing
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Resolution set to: {frame_width}x{frame_height}")

    try:
        model = YOLOWorld(model_id="yolo_world/l")
        logging.info("YOLOWorld model initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize YOLOWorld model: {e}")
        return
    classes = ["trading card"]
    model.set_classes(classes)

    frame_count = 0
    skip_frames = 3  # Process every 2nd frame

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        if frame_count % skip_frames == 0:

            results = model.infer(frame, confidence=0.03)
            detections = sv.Detections.from_inference(results)
            labels = [
                f"{classes[class_id]} {confidence:0.3f}"
                for class_id, confidence in zip(
                    detections.class_id, detections.confidence
                )
            ]
            annotated_image = frame.copy()
            BOUNDING_BOX_ANNOTATOR = sv.BoundingBoxAnnotator(thickness=2)
            LABEL_ANNOTATOR = sv.LabelAnnotator(
                text_thickness=2, text_scale=1, text_color=sv.Color.BLACK
            )
            annotated_image = BOUNDING_BOX_ANNOTATOR.annotate(
                annotated_image, detections
            )
            annotated_image = LABEL_ANNOTATOR.annotate(
                annotated_image, detections, labels=labels
            )

            # Convert BGR to RGB
            annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

            # Put the processed frame and other variables into the queue
            frame_queue.put(
                (annotated_image, detections.class_id, detections.xyxy, frame_count)
            )

        frame_count += 1

    cap.release()
    frame_queue.put(None)  # Signal the display thread to exit
