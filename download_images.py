import json
import requests
import os


def download_images_from_jsons(json_dir_path):
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

    # Iterate over each JSON file in the directory
    for json_file_name in os.listdir(json_dir_path):
        if json_file_name.endswith(".json"):
            json_file_path = os.path.join(json_dir_path, json_file_name)
            # Load the JSON data
            with open(json_file_path, "r") as json_file:
                cards = json.load(json_file)

            # Iterate over each card in the JSON list
            for card in cards:
                # Download the large image for the card
                card_id = card["id"]
                image_url = card["images"]["large"]
                save_path = os.path.join(images_dir, f"{card_id}.png")

                # Check if the image already exists
                if not os.path.exists(save_path):
                    download_image(image_url, save_path)
                else:
                    print(f"Image {save_path} already exists, skipping download.")


# Example usage
download_images_from_jsons("pokemon-tcg-data-master/cards/en/")
