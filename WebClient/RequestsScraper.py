from .ScraperFactory import ScraperFactory


class RequestsScraper(ScraperFactory):
    def __init__(self):
        self.test = None

    def get(self):
        pass

    def close(self):
        pass

    def add_response_checker(self):
        pass
