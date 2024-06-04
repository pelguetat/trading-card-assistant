import numpy as np
import torch
import torchvision.transforms as T
import faiss
from PIL import Image
import cv2
import json
from tqdm.notebook import tqdm
from matplotlib import pyplot as plt
import supervision as sv
import os
from dotenv import load_dotenv


class SimilaritySearch:
    def __init__(
        self, image_dir, json_file_path, model_name="dinov2_vits14", device_type="mps"
    ):
        load_dotenv()
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = (
            "1"  # Set the fallback environment variable
        )
        os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

        # Load the model
        self.model = torch.hub.load("facebookresearch/dinov2", model_name)

        # Select the device
        self.device = torch.device(device_type)

        # Move the model to the selected device
        self.model.to(self.device)

        print(f"Model loaded on {self.device}")

        self.files = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.lower().endswith(".png")
        ]
        self.transform_image = T.Compose(
            [T.ToTensor(), T.Resize(244), T.CenterCrop(224), T.Normalize([0.5], [0.5])]
        )
        self.index, self.all_embeddings, self.all_metadata = self.load_index()
        # self.metadata = self.extract_metadata(json_file_path)

    def load_image(self, img: str) -> torch.Tensor:
        """
        Load an image and return a tensor that can be used as an input to DINOv2.
        """
        img = Image.open(img).convert("RGB")  # Ensure the image has 3 channels
        transformed_img = self.transform_image(img).unsqueeze(0)
        return transformed_img

    def flatten_metadata(self, metadata):
        flat_metadata = {}

        def _flatten(obj, parent_key=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}_{k}" if parent_key else k
                    _flatten(v, new_key)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    new_key = f"{parent_key}_{i}" if parent_key else str(i)
                    _flatten(v, new_key)
            else:
                flat_metadata[parent_key] = obj

        _flatten(metadata)
        return flat_metadata

    def search_metadata(self, pokemon_id):
        # search all_metadata.json for pokemon_id
        return self.all_metadata.get(pokemon_id, {})

    def create_index(self) -> faiss.IndexFlatL2:
        """
        Create an index that contains all of the images in the specified list of files.
        """
        index = faiss.IndexFlatL2(384)

        all_embeddings = {}
        all_metadata = {}

        with torch.no_grad():
            for i, file in enumerate(self.files):
                print(f"Processing file {i+1}/{len(self.files)}: {file}")
                embeddings = self.model(self.load_image(file).to(self.device))
                embedding = embeddings[0].cpu().numpy()

                all_embeddings[file] = np.array(embedding).reshape(1, -1).tolist()
                all_metadata[os.path.splitext(file)[0]] = self.metadata.get(
                    os.path.splitext(os.path.basename(file))[0], {}
                )
                index.add(np.array(embedding).reshape(1, -1))

        with open("all_embeddings.json", "w") as f:
            f.write(json.dumps(all_embeddings))

        with open("all_metadata.json", "w") as f:
            f.write(json.dumps(all_metadata))

        faiss.write_index(index, "data.bin")

        return index, all_embeddings, all_metadata

    def extract_metadata(self, json_dir_path):
        card_metadata = {}

        # Iterate over all JSON files in the directory
        for json_file_name in os.listdir(json_dir_path):
            if json_file_name.endswith(".json"):
                json_file_path = os.path.join(json_dir_path, json_file_name)

                # Load the JSON data
                with open(json_file_path, "r") as json_file:
                    cards = json.load(json_file)

                # Update the dictionary to map card IDs to their metadata
                for card in cards:
                    card_metadata[card["id"]] = self.flatten_metadata(
                        {k: v for k, v in card.items() if k != "images"}
                    )

        return card_metadata

    def search_index(
        self, index: faiss.IndexFlatL2, embeddings: list, k: int = 3
    ) -> list:
        """
        Search the index for the images that are most similar to the provided image.
        """
        D, I = index.search(np.array(embeddings[0].reshape(1, -1)), k)

        results = []
        for idx in I[0]:
            file_name = self.files[idx]
            results.append(
                {
                    "file": file_name,
                    "metadata": self.search_metadata(os.path.splitext(file_name)[0]),
                }
            )

        return results

    def display_image(self, image_path):
        img = cv2.resize(cv2.imread(image_path), (416, 416))
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.show()

    def load_index(
        self,
        index_path="data.bin",
        embeddings_path="all_embeddings.json",
        metadata_path="all_metadata.json",
    ):
        """
        Load the index, embeddings, and metadata from files.
        """
        index = faiss.read_index(index_path)

        with open(embeddings_path, "r") as f:
            all_embeddings = json.load(f)

        with open(metadata_path, "r") as f:
            all_metadata = json.load(f)

        print("Index and metadata loaded successfully.")
        return index, all_embeddings, all_metadata

    def process_search_file(self, cropped_images, k=1) -> list:
        results_list = []

        for cropped_image in cropped_images:
            with torch.no_grad():
                embedding = self.model(self.load_image(cropped_image).to(self.device))
                results = self.search_index(
                    self.index, np.array(embedding[0].cpu()).reshape(1, -1), k
                )
                results_list.append(results)

        return results_list
