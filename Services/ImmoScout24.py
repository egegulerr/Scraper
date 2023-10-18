import os
from BaseIntegration import BaseIntegration
import logging
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from urllib.parse import urljoin, urlencode
from Repository.ImmoScoutRepository import ImmoScoutDB
from Entity.UserImmoScout import User

logging.basicConfig(level=logging.INFO)


class ImmoScout24(BaseIntegration):
    def __init__(self, use_selenium=False, webdriver_options=None):
        super().__init__(use_selenium, webdriver_options)
        self.url = "https://www.immobilienscout24.de/"
        self.login_xpath = ".//*[text()='Anmelden'][self::a or self::span]"
        self.captcha_xpath = (
            ".//div[@class='main__captcha']//p[contains(text(), 'Nachdem du das unten stehende CAPTCHA "
            "bestätigt hast')] | .//span[contains(text(), 'Captcha')]"
        )
        self.username = os.environ["USERNAME"]
        self.password = os.environ["PASSWORD"]
        self.db = ImmoScoutDB()

    def setup(self):
        self.scraper.add_response_checker(self.response_checker)

    def response_checker(self, response_body):
        if response_body.xpath(self.captcha_xpath):
            logging.info("Captcha showed up. Solving it")
            self.scraper.solve_recaptcha()

    @staticmethod
    def get_search_url(search_details):
        return urljoin(
            "https://www.immobilienscout24.de/Suche/de/bayern/muenchen/wohnung-mieten",
            "?" + urlencode(search_details),
        )

    def login(self):
        logging.info("Doing login")
        # TODO Maybe need to wait, sometimes robots check comes before cookies
        self.scraper.get(self.url)
        self.scraper.handle_cookies()
        self.scraper.find_and_click_element(By.XPATH, self.login_xpath)
        self.scraper.find_and_send_key(
            By.XPATH, ".//input[@id='username']", self.username
        )
        self.scraper.find_and_click_element(By.ID, "submit")
        self.scraper.find_and_send_key(By.ID, "password", self.password)
        self.scraper.find_and_click_element(By.ID, "loginOrRegistration")
        email_code_list = self.scraper.find_elements(By.XPATH, './/*[@name="answer"]')
        if len(email_code_list) == 1:
            logging.info("2FA Found. Solving it")
            self.do_2fa(email_code_list[0])
        self.scraper.get(self.url)

    def do_2fa(self, input_field):
        code = input("Give the 2FA code from the from email")
        input_field.send_keys(code)
        sleep(3)
        self.scraper.find_and_click_element(By.XPATH, ".//input[@value='Bestätigen']")

    def scrape_houses(self, url):
        def get_element_info(element, key):
            return element.find_element(
                By.XPATH, f".//dl/dt[text()='{key}']/preceding-sibling::dd[1]"
            ).text

        logging.info("Search started")

        self.scraper.get(url)
        pager_xpath = ".//div[@data-testid='pager']//li"
        last_page_number = int(
            self.scraper.find_element(By.XPATH, f"{pager_xpath}[last()-1]").text
        )
        result = []
        for page_number in range(1, last_page_number + 1):
            logging.info(f"Scrapin page: {page_number} out of {last_page_number}")
            if page_number >= 2:
                self.scraper.click_when_clickable(
                    By.XPATH,
                    f"{pager_xpath}/a[contains(@aria-label, 'Page {page_number}')]",
                )
            articles = self.scraper.find_elements(
                By.XPATH,
                ".//ul[@id='resultListItems']/li[@data-id]/article[not(.//button[contains(@class, "
                "'heart_24_filled')])]",
            )

            for article in articles:
                # TODO need to implement premium houses
                if "paywall-listing" in article.get_attribute("class"):
                    continue

                attributes = article.find_element(
                    By.XPATH, ".//div[contains(@data-is24-qa, 'attributes')]"
                )
                result.append(
                    {
                        "link": article.find_element(
                            By.XPATH, ".//div[@class='result-list-entry__data']//a"
                        ).get_attribute("href"),
                        "WarmMiete": get_element_info(attributes, "Warmmiete"),
                        "Area": get_element_info(attributes, "Wohnfläche"),
                        "Address": article.find_element(
                            By.XPATH,
                            ".//button[contains(@title, 'Auf der Karte anzeigen')]",
                        ).text,
                    }
                )
            sleep(2)
        return result

    def send_message(self, house_title, house_owner, user_details):
        def select_option(select_name, option_value):
            Select(self.scraper.find_element(By.NAME, select_name)).select_by_value(
                option_value
            )

        def fill_form():
            owner_parsed = house_owner.split(" ")
            gender, last_name = owner_parsed[0], owner_parsed[-1]
            message = User.get_email_template(gender, last_name)
            self.scraper.click_when_clickable(By.XPATH, ".//a[@data-qa='sendButton']")
            sleep(2)
            self.scraper.find_and_send_key(By.ID, "contactForm-Message", message)

            if not self.scraper.find_element(By.NAME, "moveInDateType").is_displayed():
                return

            select_option("moveInDateType", user_details["moveInDateType"])
            select_option("numberOfPersons", user_details["numberOfPersons"])
            select_option("hasPets", user_details["hasPets"])
            select_option(
                "employmentRelationship", user_details["employmentRelationship"]
            )
            select_option("income", user_details["income"])
            select_option(
                "applicationPackageCompleted",
                user_details["applicationPackageCompleted"],
            )

        logging.info(
            f"Extracted details of {house_title}. Sending message now to owner {house_owner}"
        )

        sleep(3)
        fill_form()
        self.scraper.click_when_clickable(
            By.XPATH, ".//button[@data-qa='sendButtonBasic']", time_out=60
        )
        logging.info(f"Message successfully sent")

    def get_detail(self, houses):
        result = []
        for house in houses:
            logging.info("Got the house information. Getting details")
            self.scraper.get(house["link"])
            # TODO Maybe dont need to scrape with driver. IS24 File could be used ?

            description_elements = self.scraper.find_elements(
                By.XPATH,
                ".//div[@id='is24-content']/div[contains(@class, "
                "'contact-box')]/following-sibling::div[1]//div["
                "contains(@class, 'is24-text')]",
            )
            description_texts = [element.text for element in description_elements]
            title = self.scraper.find_element(By.ID, "expose-title").text
            owner = self.scraper.find_element(
                By.XPATH, ".//div[@data-qa='contactName']"
            ).text
            house_details = {
                **house,
                "title": title,
                "owner": owner,
                "description": description_texts,
                "Rooms": self.scraper.find_element(
                    By.XPATH, ".//div[contains(@class, 'zi-main')]"
                ).text,
            }
            result.append(house_details)
        return result

    def contact_owner(self, houses):
        contacted_houses = []
        for house in houses:
            user_form_details = User.get_form_details()
            try:
                self.send_message(house["title"], house["owner"], user_form_details)
                contacted_houses.append(house)
            except Exception as e:
                logging.error(f"An error occured while sending the message: {e}")

        return contacted_houses

    def scrape(self):
        try:
            self.login()
            # TODO Maybe dont need connect function here ?
            self.db.connect()
            houses = self.db.get_founded_houses()

            if houses:
                logging.info("There are already scraped houses.")
                houses_detailed = self.get_detail(houses)
                contacted_houses = self.contact_owner(houses_detailed)
            else:
                user_search_details = User.get_search_details()
                url = self.get_search_url(user_search_details)
                houses = self.scrape_houses(url)
                self.db.insert_founded_houses(houses)
                houses_detailed = self.get_detail(houses)
                contacted_houses = self.contact_owner(houses_detailed)

            self.db.delete_founded_houses(contacted_houses)
            self.db.insert_contacted_houses(contacted_houses)

        except Exception as e:
            logging.error(f"An error occured while scraping: {e}")
        finally:
            self.db.close()