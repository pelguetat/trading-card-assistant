from __future__ import annotations

import cv2
import numpy as np
import os
import json
from matplotlib import pyplot as plt
from collections.abc import Iterable
import concurrent.futures
import itertools
import pickle

class Match:
    def __init__(self, pokemon_id: str, count: int) -> None:
        self.pokemon_id = pokemon_id
        self.count = count

    @staticmethod
    def findBest(matches: Iterable[Match | None]) -> Match | None:
        bestMatch = None
        for match in matches:
            if match == None:
                continue
            if bestMatch == None or match.count > bestMatch.count:
                bestMatch = match
        return bestMatch

class SimilaritySearch:
    def __init__(self, image_dir):
        self.orb = cv2.ORB_create()
        self.files = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.lower().endswith(".png")
        ]
        self.image_dir = image_dir
        self.descriptors = self.load_descriptors()
        self.processExecutor = concurrent.futures.ProcessPoolExecutor()

    @staticmethod
    def compare(pokemon_id: str, des1: np.ndarray, des2: np.ndarray) -> Match | None:
        # FLANN parameters
        FLANN_INDEX_LSH = 6
        index_params= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6,
                           key_size = 12,
                           multi_probe_level = 1)
        search_params = dict(checks=10)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)

        good_matches = 0
        for match in matches:
            if len(match) >= 2:
                m, n = match
                if m.distance < 0.7 * n.distance:
                    good_matches += 1


        if good_matches == 0:
            return None
        return Match(pokemon_id, good_matches)

    def identify(self, img) -> Match | None:
        _, des = self.orb.detectAndCompute(img, None)
        imageDescription: np.ndarray = des
        pokemon_ids: list[str] = []
        imageDescriptions: Iterable[np.ndarray] = itertools.cycle([imageDescription])
        cardDescriptions: list[np.ndarray] = []
        for pokemon_id, cardDescription in self.descriptors.items():
            pokemon_ids.append(pokemon_id)
            cardDescriptions.append(cardDescription)
        futures = self.processExecutor.map(
            SimilaritySearch.compare, pokemon_ids, imageDescriptions, cardDescriptions
        )
        best_match = Match.findBest(futures)
        if best_match is not None:
            print(f"Identified Pokemon ID: {best_match.pokemon_id}")
            self.display_image(best_match.pokemon_id)
        return best_match


    def load_descriptors(self) -> dict[str, np.ndarray]:
        if os.path.exists('descriptors.pkl'):
            with open('descriptors.pkl', 'rb') as f:
                descriptors = pickle.load(f)
        else:
            descriptors = {}
            for file in self.files:
                img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
                _, des = self.orb.detectAndCompute(img, None)
                pokemon_id = os.path.splitext(os.path.basename(file))[0]
                descriptors[pokemon_id] = des
            with open('descriptors.pkl', 'wb') as f:
                pickle.dump(descriptors, f)
        return descriptors

    def reload_descriptors(self) -> None:
        if os.path.exists('descriptors.pkl'):
            os.remove('descriptors.pkl')
        self.descriptors = self.load_descriptors()

    def display_image(self, pokemon_id):
        image_path = os.path.join(self.image_dir, pokemon_id + '.png')
        img = cv2.imread(image_path)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.show()

    def process_search_file(self, cropped_images) -> list:
        results_list = []
        for cropped_image in cropped_images:
            img = cv2.imread(cropped_image, cv2.IMREAD_GRAYSCALE)
            results = self.identify(img)
            results_list.append(results)
        return results_list