from Scraper import Scraper
from abc import ABC, abstractmethod


class BaseIntegration(ABC):
    def __init__(self):
        self.scraper = Scraper()

    @abstractmethod
    def response_checker(self, response):
        raise NotImplementedError("Response checker not implemented!")

    @abstractmethod
    def scrape(self):
        raise NotImplementedError("Scrape function is not implemented!")
