import cv2
from ultralytics import YOLOWorld
import numpy as np

# Capture video from the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video stream")
else:
    model = YOLOWorld(model="yolov8l-worldv2.pt", verbose=False)
    model.set_classes(["pokemon trading card"])
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        # Rotate the frame if necessary

        results = model.predict(frame, device="mps")
        result = results[0]
        boxes = result.boxes.xyxy
        bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
        classes = np.array(result.boxes.cls.cpu(), dtype="int")
        print(boxes)
        for cls, bbox in zip(classes, bboxes):
            (x, y, x2, y2) = bbox
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 225), 2)
            cv2.putText(
                frame, str(cls), (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 225), 2
            )
        cv2.imshow("Video Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
