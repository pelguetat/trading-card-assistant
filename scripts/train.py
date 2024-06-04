from ultralytics import YOLO

# Load a model
model = YOLO(
    "runs/detect/train3/weights/last.pt"
)  # load a pretrained model (recommended for training)

# Train the model with 2 GPUs
results = model.train(
    data="dataset.yaml",
    epochs=100,
    imgsz=800,
    device="mps",
    workers=3,
    resume=True,
)
