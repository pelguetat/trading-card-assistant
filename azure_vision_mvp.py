import os
import time
import uuid

# isort: off
from azure.cognitiveservices.vision.customvision.training import (
    CustomVisionTrainingClient,
)
from dotenv import load_dotenv
from msrest.authentication import ApiKeyCredentials
from azure.cognitiveservices.vision.customvision.prediction import (
    CustomVisionPredictionClient,
)
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageFileCreateBatch,
    ImageFileCreateEntry,
    Region,
)

# isort: on

load_dotenv()
# Replace with valid values

ENDPOINT = os.getenv("VISION_TRAINING_ENDPOINT")
training_key = os.getenv("VISION_TRAINING_KEY")
prediction_key = os.getenv("VISION_PREDICTION_KEY")
prediction_resource_id = os.getenv("VISION_PREDICTION_RESOURCE_ID")

credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
prediction_credentials = ApiKeyCredentials(
    in_headers={"Prediction-key": prediction_key}
)
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)
publish_iteration_name = "detectModel"

# Find the object detection domain
obj_detection_domain = next(
    domain
    for domain in trainer.get_domains()
    if domain.type == "ObjectDetection" and domain.name == "General"
)

# Create a new project
print("Creating project...")
# Use uuid to avoid project name collisions.
project = trainer.create_project(str(uuid.uuid4()), domain_id=obj_detection_domain.id)
