from typing import cast
import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
from chromadb import EmbeddingFunction, Embeddings
from chromadb.api.types import Images


class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Images) -> Embeddings:
        return cast(Embeddings, [vectorize_image(image) for image in input])


# chroma_client.delete_collection("pokemon_cards")
embedding_function = MyEmbeddingFunction()
data_loader = ImageLoader()

chroma_client = chromadb.PersistentClient(path="chromadb")
collection = chroma_client.create_collection(
    name="pokemon_cards", embedding_function=embedding_function, data_loader=data_loader
)


def vectorize_image(url: str):
    import requests

    # Define the endpoint and parameters
    endpoint = "https://pokemon-cards.cognitiveservices.azure.com/computervision/retrieval:vectorizeImage"
    api_version = "2024-02-01"
    model_version = "2023-04-15"
    subscription_key = "b365927a9ad0473fa1d4054ecd6a77c8"

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key,
    }

    # Define the data payload
    data = {"url": url}

    # Make the POST request
    response = requests.post(
        f"{endpoint}?api-version={api_version}&model-version={model_version}",
        headers=headers,
        json=data,
    )

    # Print the response
    print(response.status_code)
    print(response.json())
    response = response.json()
    return response["vector"]


# Example usage
