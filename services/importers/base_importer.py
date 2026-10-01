from abc import ABC, abstractmethod


class BaseImporter(ABC):

    @abstractmethod
    def import_products(self):
        """Return a list of products"""
        pass