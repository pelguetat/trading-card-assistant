import json
import requests
import os
import chromadb


import json
import requests
import os


def download_images_and_save_metadata(base_dir):
    # Directory to save the images
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)

    # Function to download an image
    def download_image(url, save_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, "wb") as img_file:
                img_file.write(response.content)
            print(f"Downloaded {save_path}")
        else:
            print(f"Failed to download {url}")

    # Iterate over each JSON file in the base directory
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                json_file_path = os.path.join(root, file)

                # Load the JSON data
                with open(json_file_path, "r") as json_file:
                    cards = json.load(json_file)

                # Iterate over each card in the JSON list
                for card in cards:
                    # Download the large image for the card
                    card_id = card["id"]
                    image_url = card["images"]["large"]
                    save_path = os.path.join(images_dir, f"{card_id}.png")
                    download_image(image_url, save_path)

                    # Save the rest of the data as metadata
                    metadata = {k: v for k, v in card.items() if k != "images"}
                    metadata_path = os.path.join(images_dir, f"{card_id}_metadata.json")
                    with open(metadata_path, "w") as metadata_file:
                        json.dump(metadata, metadata_file, indent=4)
                    print(f"Saved metadata for {card_id}")


# Call the function with the base directory path
download_images_and_save_metadata("pokemon-tcg-data-master/cards")


def vectorize_cards():
    # Load the ChromaDB client
    chroma_client = chromadb.PersistentClient(path="chromadb")
    collection = chroma_client.get_collection("pokemon_cards")

    # Get the list of card names
    card_names = collection.get_card_names()

    # Create a directory to save the vectorized images
    output_dir = "vectorized_images"
    os.makedirs(output_dir, exist_ok=True)

    # Vectorize each card
    for card_name in card_names:
        # Get the image URL for the card
        image_url = collection.get_image_url(card_name)

        # Download the image
        image_path = os.path.join(output_dir, f"{card_name}.jpg")
        download_image(image_url, image_path)

        # Vectorize the image
        embedding = collection.get_embedding(card_name)
        with open(os.path.join(output_dir, f"{card_name}.json"), "w") as f:
            json.dump(embedding, f)

    print("Vectorization completed.")
