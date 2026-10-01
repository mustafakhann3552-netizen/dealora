import json
import os

from services.importers.base_importer import BaseImporter


class JSONImporter(BaseImporter):

    def __init__(self, file_path="data/products.json"):
        self.file_path = file_path

    def import_products(self):

        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)