import logging

from WebClient.SeleniumScraper import SeleniumScraper
from WebClient.RequestsScraper import RequestsScraper
from Integrations.immoScout24.service.ScrapingService import ScrapingService
from Integrations.immoScout24.entity.UserImmoScout import User
from Integrations.immoScout24.repository.ImmoScoutRepository import ImmoScoutDB
from Integrations.immoScout24.ImmoScout24 import ImmoScout24


def create_scraper_instance(use_selenium=False):
    return SeleniumScraper() if use_selenium else RequestsScraper()


if __name__ == "__main__":
    user_entity = User.from_env()
    repository = ImmoScoutDB()

    while True:
        try:
            driver = create_scraper_instance(use_selenium=True)
            rest = create_scraper_instance(use_selenium=False)

            scraping_service = ScrapingService(webdriver=driver, rest=rest)

            main_script = ImmoScout24(scraping_service, user_entity, repository)
            main_script.main()
        except Exception as e:
            logging.error(f"ERROR: {e}")
            answer = input("Error occured. Do you want to start again ? Y/N")
            scraping_service.close()
            if answer.lower() == "n":
                logging.info("************TERMINATING************")
                break

    print("Done")
