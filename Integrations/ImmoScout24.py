import os
from BaseIntegration import BaseIntegration
import logging
from time import sleep
from selenium.webdriver.common.by import By
from urllib.parse import urljoin, urlencode

# Configure the logger
logging.basicConfig(level=logging.INFO)


class ImmoScout24(BaseIntegration):
    url = "https://www.immobilienscout24.de/"
    login_xpath = ".//*[text()='Anmelden'][self::a or self::span]"
    captcha_xpath = (
        ".//div[@class='main__captcha']//p[contains(text(), 'Nachdem du das unten stehende CAPTCHA "
        "bestätigt hast')] | .//span[contains(text(), 'Captcha')]"
    )
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    email_name = "Mehmet"
    email_lastname = "Simsek"

    def __init__(self, use_selenium=False, webdriver_options=None):
        super().__init__(use_selenium, webdriver_options)

    def setup(self):
        self.scraper.add_response_checker(self.response_checker)

    def response_checker(self, response_body):
        if response_body.xpath(self.captcha_xpath):
            logging.info("Captcha showed up. Solving it")
            self.scraper.solve_recaptcha()

    @staticmethod
    def get_search_url():
        return urljoin(
            "https://www.immobilienscout24.de/Suche/de/bayern/muenchen/wohnung-mieten",
            "?"
            + urlencode(
                {
                    "numberofrooms": "1.5-",
                    "price": "-900.0",
                    "pricetype": "rentpermonth",
                    "enteredFrom": "one_step_search",
                }
            ),
        )

    @staticmethod
    def get_email_text(gender, name):
        # TODO Maybe storing email with json or creating class for E-Mail could be a good idea
        # email_text = f"""Sehr geehrte {gender} {last_name},
        # Ich bin {self.email_name}. Ich liebe Bayern München.
        #
        # Mit freundlichen Grüßen,
        # {self.email_name} {self.email_lastname}"""
        return "Test"

    def login(self):
        logging.info("Doing login")
        self.scraper.get(self.url)
        cookie_button = self.scraper.execute_script(
            """return  document.querySelector('#usercentrics-root').shadowRoot.querySelector("button[data-testid='uc-accept-all-button']")"""
        )
        self.scraper.click_element(cookie_button)
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

    def get_general_home_info(self, url):
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
                By.XPATH, ".//ul[@id='resultListItems']/li[@data-id]/article"
            )

            for article in articles:
                isPremiumRequired = "paywall-listing" in article.get_attribute("class")
                # TODO need to implement premium houses
                if isPremiumRequired:
                    continue
                result.append(
                    {
                        "link": article.find_element(
                            By.XPATH, ".//div[@class='result-list-entry__data']//a"
                        ).get_attribute("href"),
                    }
                )
            sleep(2)
        return result

    def get_house_details(self, house_info):
        logging.info("Got the house information. Getting details")
        self.scraper.get(house_info["link"])
        # TODO Maybe dont need to scrape with driver. IS24 File could be used ?
        house = {
            **house_info,
            "address": self.scraper.find_element(
                By.XPATH, './/span[@class="zip-region-and-country"]'
            ).text,
            "kaltMiete": self.scraper.find_element(
                By.XPATH,
                ".//div[contains(@class,'kaltmiete')]/span[contains(@class, 'preis-value')]",
            ).text,
            "warmMiete": self.scraper.find_element(
                By.XPATH, ".//div[contains(@class,'warmmiete-main is24-value')]"
            ).text,
            "numberOfRooms": self.scraper.find_element(
                By.XPATH, ".//div[contains(@class, 'zi-main')]"
            ).text,
            "quadratMeter": self.scraper.find_element(
                By.XPATH, ".//div[contains(@class, 'flaeche-main is24-value')]"
            ).text,
        }
        description_elements = self.scraper.find_elements(
            By.XPATH,
            ".//div[@id='is24-content']/div[contains(@class, "
            "'contact-box')]/following-sibling::div[1]//div["
            "contains(@class, 'is24-text')]",
        )
        decription_texts = [element.text for element in description_elements]
        title = self.scraper.find_element(By.ID, "expose-title").text
        owner = self.scraper.find_element(
            By.XPATH, ".//div[@data-qa='contactName']"
        ).text
        house.update({"title": title, "owner": owner, "desccription": decription_texts})
        return house

    def send_message(self, house_title, house_owner):
        def fill_form():
            message = self.get_email_text(gender, last_name)
            self.scraper.find_and_send_key(By.ID, "contactForm-Message", message)

        logging.info(
            f"Extracted details of {house_title}. Sending message now to owner {house_owner}"
        )
        sleep(3)
        self.scraper.click_when_clickable(By.XPATH, ".//a[@data-qa='sendButton']")
        owner_parsed = house_owner.split(" ")
        gender, last_name = owner_parsed[0], owner_parsed[-1]
        fill_form()
        self.scraper.click_when_clickable(
            By.XPATH, ".//button[@data-qa='sendButtonBasic']", time_out=60
        )

    def scrape(self):
        self.login()
        url = self.get_search_url()
        house_infos = self.get_general_home_info(url)
        for house_info in house_infos:
            house = self.get_house_details(house_info)
            # TODO Maybe house can be saved into database ?
            self.send_message(house["title"], house["owner"])
