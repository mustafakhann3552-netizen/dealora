from services.importers.json_importer import JSONImporter
from services.importers.csv_importer import CSVImporter


class ImportManager:

    def __init__(self):

        self.importers = {
            "json": JSONImporter,
            "csv": CSVImporter,
        }

    def get_importer(self, source_type, *args, **kwargs):

        importer = self.importers.get(source_type)

        if importer is None:
            raise Exception(f"Unsupported importer: {source_type}")

        return importer(*args, **kwargs)