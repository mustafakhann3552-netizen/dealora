import json
import os


class ProductFetcher:

    def __init__(self):
        self.file = "data/products.json"

    def get_next_product(self):

        if not os.path.exists(self.file):
            return None

        with open(self.file, "r", encoding="utf-8") as f:
            products = json.load(f)

        if len(products) == 0:
            return None

        # First product nikalo
        product = products.pop(0)

        # Updated list wapas save karo
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4)

        return product