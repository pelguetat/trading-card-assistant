import json
from PIL import Image
import imagehash
import os
from annoy import AnnoyIndex

class ImageSimilaritySearch:
    def __init__(self, image_dir):
        self.image_dir = image_dir
        self.index = "image_index.ann"
        if not os.path.exists('image_hashes.json') or os.path.getsize('image_hashes.json') == 0:
                    self.image_hashes = self.compute_hashes()
        else:
            with open('image_hashes.json', 'r') as file:
                self.image_hashes = json.load(file)
    def compute_hashes(self, limit=None):
        image_hashes = {}
        image_files = os.listdir(self.image_dir)
        
        # If limit is specified and less than the number of image files, reduce the list
        if limit is not None and limit < len(image_files):
            image_files = image_files[:limit]
            
        for image_file in image_files:
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(self.image_dir, image_file)
                image = Image.open(image_path)
                image_hash = imagehash.average_hash(image)
                # Convert numpy array to list before storing in dictionary
                image_hashes[image_file] = image_hash.hash.flatten().tolist()
        with open('image_hashes.json', 'w') as file:
            json.dump(image_hashes, file)
        return image_hashes

    def create_index(self):
        index = AnnoyIndex(64, 'hamming')  # Length of item vector that will be indexed
        for i, image_hash in enumerate(self.image_hashes.values()):
            index.add_item(i, image_hash)
        index.build(10)  # 10 trees
        index.save('image_index.ann')  # Save the index to a file
        return index

    def find_similar_images(self, image_path, n=5):
        image = Image.open(image_path)
        image_hash = imagehash.average_hash(image, hash_size=16).hash.flatten()

        if not os.path.exists(self.index):
            self.create_index()

        index = AnnoyIndex(64, 'hamming')
        index.load(self.index)

        similar_images = []
        nearest_ids = index.get_nns_by_vector(image_hash, n)
        for nearest_id in nearest_ids:
            similar_image_file = list(self.image_hashes.keys())[nearest_id]
            similar_images.append(similar_image_file)

        return similar_images