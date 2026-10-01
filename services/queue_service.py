from services.importers.json_importer import JSONImporter
import json


class QueueService:

    def __init__(self):

        self.importer = JSONImporter()
        self.file = "data/products.json"

    def peek(self):

        products = self.importer.import_products()

        if not products:
            return None

        return products[0]

    def remove(self):

        products = self.importer.import_products()

        if not products:
            return

        products.pop(0)

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4)

            def add(self, product):

                products = self.importer.import_products()

                products.append(product)

                with open(self.file, "w", encoding="utf-8") as f:
                    json.dump(products, f, indent=4)