from WebClient.SeleniumScraper import SeleniumScraper
from WebClient.RequestsScraper import RequestsScraper
from Integrations.immoScout24.service.ScrapingService import ScrapingService
from Integrations.immoScout24.entity.UserImmoScout import User
from Integrations.immoScout24.repository.ImmoScoutRepository import ImmoScoutDB
from Integrations.immoScout24.ImmoScout24 import ImmoScout24


def create_scraper_instance(use_selenium=False, web_driver_options=None):
    return SeleniumScraper(web_driver_options) if use_selenium else RequestsScraper()


if __name__ == "__main__":
    driver = create_scraper_instance(use_selenium=True)
    rest = create_scraper_instance(use_selenium=False)

    user_entity = User.from_env()
    repository = ImmoScoutDB()
    scraping_service = ScrapingService(webdriver=driver, rest=rest)

    main_script = ImmoScout24(scraping_service, user_entity, repository)
    main_script.main()

    print("Done")
