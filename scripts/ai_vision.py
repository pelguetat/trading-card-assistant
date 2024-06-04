import os
import requests
from dotenv import load_dotenv

load_dotenv()


def upload_dataset():
    url = (
        f"{os.getenv('AI_VISION_ENDPOINT')}/computervision/datasets/pythondataset2"
        "?api-version=2023-02-01-preview"
    )
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": os.getenv("AI_VISION_KEY"),
    }
    data = {
        "annotationKind": "imageObjectDetection",
        "annotationFileUris": [
            "https://storage543646.blob.core.windows.net/coco/coco_file.json"
        ],
        "authenticationKind": {
            "kind": "sas",
            "sasToken": "sp=r&st=2024-05-23T16:06:48Z&se=2024-05-24T00:06:48Z&sv=2022-11-02&sr=b&sig=rr8UKlKPGBvCUwZVnHBW79AdRkqOmaE%2FtTe2WFOAoeU%3D",
        },
    }

    response = requests.put(url, headers=headers, json=data)

    print(response.status_code)
    print(response.json())


def train_model(endpoint, model_name, subscription_key, dataset_name):
    url = (
        f"{endpoint}/computervision/models/{model_name}?api-version=2023-02-01-preview"
    )
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key,
    }
    data = {
        "trainingParameters": {
            "trainingDatasetName": dataset_name,
            "timeBudgetInHours": 1,
            "modelKind": "Generic-Detector",
        }
    }

    response = requests.put(url, headers=headers, json=data)

    print(response.status_code)
    print(response.json())


# train_model(
#     os.getenv("AI_VISION_ENDPOINT"),
#     "pythonmodel",
#     os.getenv("AI_VISION_KEY"),
#     "pythondataset",
# )
upload_dataset()
