import csv

from services.importers.base_importer import BaseImporter


class CSVImporter(BaseImporter):

    def __init__(self, file_path):
        self.file_path = file_path

    def import_products(self):

        with open(self.file_path, "r", encoding="utf-8-sig", newline="") as file:

            reader = csv.DictReader(file)

            for row in reader:

                yield {
                    "title": row.get("title", "").strip(),
                    "brand": row.get("brand", "").strip(),
                    "category": row.get("category", "").strip(),
                    "price": float(row.get("price", 0) or 0),
                    "old_price": float(row.get("old_price", 0) or 0),
                    "discount": int(row.get("discount", 0) or 0),
                    "description": row.get("description", "").strip(),
                    "image": row.get("image", "").strip(),
                    "affiliate_url": row.get("affiliate_url", "").strip(),
                }