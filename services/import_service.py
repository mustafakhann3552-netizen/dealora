from services.import_manager import ImportManager
from services.queue_service import QueueService


class ImportService:

    def __init__(self):
        self.manager = ImportManager()
        self.queue = QueueService()

    def import_csv(self, file_path):

        importer = self.manager.get_importer(
            "csv",
            file_path=file_path
        )

        count = 0

        for product in importer.import_products():

            self.queue.add(product)
            count += 1

        return count