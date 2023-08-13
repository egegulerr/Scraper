from abc import ABC, abstractmethod


class ScraperFactory(ABC):
    @abstractmethod
    def get(self, url):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def add_response_checker(self):
        pass
