import logging
from Integrations.immoScout24.repository import ImmoScoutRepository
from Integrations.immoScout24.service import ImmoScoutScraper

logging.basicConfig(level=logging.INFO)


class ImmoScout24:
    def __init__(self, scraping_service, user, repository):
        # TODO Create interfaces to make dependency injection better
        self.scraper: ImmoScoutScraper = scraping_service
        self.db: ImmoScoutRepository = repository
        self.user = user

    @staticmethod
    def get_appeal(owner: str):
        owner_parsed = owner.split(" ")
        gender, last_name = owner_parsed[0], owner_parsed[-1]
        return f"{gender} {last_name}"

    def scrape(self):
        self.scraper.login()
        self.db.connect()
        houses = self.db.get_founded_houses()

        if not houses:
            user_search_details = self.user.get_search_details()
            url = self.scraper.get_search_url(user_search_details)
            houses = self.scraper.scrape_houses(url)
            self.db.insert_founded_houses(houses)
        else:
            logging.info("There are already scraped houses.")

        for house in houses:
            houses_detailed = self.scraper.get_detail(house)
            if not houses_detailed:
                self.db.delete_founded_house(house)
                continue

            form_details = self.user.get_form_details()
            email_template = self.user.get_email_template()
            appeal = self.get_appeal(houses_detailed["owner"])

            message = email_template % (
                appeal,
                self.user.name,
                self.user.age,
                self.user.experience,
                self.user.subject,
                self.user.university,
                self.user.job,
                self.user.phone,
                self.user.name,
            )

            self.scraper.contact_owner(
                houses_detailed["owner"],
                houses_detailed["Address"],
                form_details,
                message,
            )
            self.db.delete_founded_house(house)
            self.db.insert_contacted_house(houses_detailed)

    def main(self):
        while True:
            try:
                self.scrape()
            except Exception as e:
                logging.error(f"ERROR: {e}")
                answer = input("Error occured. Do you want to start again ? Y/N")
                if answer.lower() == "n":
                    logging.info("************TERMINATING************")
                    break
            finally:
                self.db.close()
