from abc import ABC, abstractmethod
from WebClient.SeleniumScraper import SeleniumScraper
from WebClient.RequestsScraper import RequestsScraper


def create_scraper_instance(use_selenium=False, web_driver_options=None):
    return SeleniumScraper(web_driver_options) if use_selenium else RequestsScraper()


class BaseIntegration(ABC):
    def __init__(self, use_selenium=False, webdriver_options=None):
        self.scraper = create_scraper_instance(use_selenium, webdriver_options)

    def response_checker(self, response):
        raise NotImplementedError("Response checker not implemented!")

    @abstractmethod
    def scrape(self):
        raise NotImplementedError("Scrape function is not implemented!")
