from abc import ABC, abstractmethod
from WebClient.SeleniumScraper import SeleniumScraper
from WebClient.RequestsScraper import RequestsScraper


def create_scraper_instance(use_selenium=False, web_driver_options=None):
    return SeleniumScraper(web_driver_options) if use_selenium else RequestsScraper()


class BaseIntegration(ABC):
    @abstractmethod
    def response_checker(self, response):
        raise NotImplementedError("Response checker not implemented!")

    @abstractmethod
    def login(self):
        raise NotImplementedError("Login function is not implemented!")

    @abstractmethod
    def setup(self):
        raise NotImplementedError("Setup function is not implemented!")
