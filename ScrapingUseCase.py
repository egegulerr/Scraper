from abc import ABC, abstractmethod
from WebClient.SeleniumScraper import SeleniumScraper
from WebClient.RequestsScraper import RequestsScraper


class ScrapingUseCase(ABC):
    @abstractmethod
    def response_checker(self, response):
        raise NotImplementedError("Response checker not implemented!")

    @abstractmethod
    def login(self):
        raise NotImplementedError("Login function is not implemented!")

    @abstractmethod
    def setup(self):
        raise NotImplementedError("Setup function is not implemented!")
