import logging
import os
from abc import ABC
from time import sleep
from typing import Type
from urllib.parse import urljoin, urlencode
from ScrapingUseCase import ScrapingUseCase
from selenium.webdriver.common.by import By
from ML.CaptchaReader import CaptchaReader
from WebClient import SeleniumScraper, RequestsScraper
from Integrations.immoScout24.service.FormFillingService import (
    FormFiller,
    SmokerForm,
    FormFillingStrategy,
    InterviewForm,
    EasyForm,
)

LOGIN_XPATH = ".//*[text()='Anmelden'][self::a or self::span]"
BOT_DETECTION_XPATH = (
    ".//div[@class='main__captcha']//p[contains(text(), 'Nachdem du das unten stehende CAPTCHA "
    "bestätigt hast')] | .//span[contains(text(), 'Captcha')]"
)
CAPTCHA_XPATH = ".//img[contains(@src, 'captcha')]"
NOT_ACTIVE_XPATH = ".//h3[text()='Angebot wurde deaktiviert']"


logging.basicConfig(level=logging.INFO)


class ScrapingService(ScrapingUseCase, ABC):
    def __init__(self, webdriver, rest, captcha_reader):
        self.url = "https://www.immobilienscout24.de/"
        self.username = os.environ["USERNAME"]
        self.password = os.environ["PASSWORD"]
        self.form_filler: FormFiller = None
        self.webdriver: SeleniumScraper = webdriver
        self.rest: RequestsScraper = rest
        self.captcha_reader: CaptchaReader = captcha_reader
        self.setup()

    def setup(self):
        self.webdriver.add_response_checker(self.response_checker)
        self.webdriver.init_driver()

    def close(self):
        self.webdriver.close()
        self.rest.close()

    def set_form_filler(self, strategy: Type[FormFillingStrategy]):
        self.form_filler = FormFiller(strategy(self.webdriver))

    def response_checker(self, response_body):
        if response_body.xpath(BOT_DETECTION_XPATH):
            logging.info("Captcha showed up. Solving it")
            self.webdriver.solve_recaptcha()
        if response_body.xpath(CAPTCHA_XPATH):
            logging.info("Captcha showed up. Solving it")
            self.solve_captcha()

    @staticmethod
    def get_search_url(search_details):
        return urljoin(
            "https://www.immobilienscout24.de/Suche/de/bayern/muenchen/wohnung-mieten",
            "?" + urlencode(search_details),
        )

    def solve_captcha(self):
        img = self.webdriver.find_element(By.XPATH, CAPTCHA_XPATH)
        path = self.webdriver.take_screenshot(img)
        text = self.captcha_reader.detect_text(path)
        self.webdriver.find_and_send_key(By.XPATH, "xpath", text)
        self.webdriver.find_and_click_element(By.XPATH, "xpath")

    def do_2fa(self, input_field):
        code = input("Give the 2FA code from the from email")
        input_field.send_keys(code)
        sleep(3)
        self.webdriver.find_and_click_element(By.XPATH, ".//input[@value='Bestätigen']")

    def login(self):
        logging.info("Doing login")
        # TODO Maybe need to wait, sometimes robots check comes before cookies
        self.webdriver.get(self.url)
        self.webdriver.handle_cookies()
        self.webdriver.find_and_click_element(By.XPATH, LOGIN_XPATH)
        self.webdriver.find_and_send_key(
            By.XPATH, ".//input[@id='username']", self.username
        )
        self.webdriver.find_and_click_element(By.ID, "submit")
        self.webdriver.find_and_send_key(By.ID, "password", self.password)
        self.webdriver.find_and_click_element(By.ID, "loginOrRegistration")
        email_code_list = self.webdriver.find_elements(By.XPATH, './/*[@name="answer"]')
        if len(email_code_list) == 1:
            logging.info("2FA Found. Solving it")
            self.do_2fa(email_code_list[0])
        self.webdriver.get(self.url)

    def scrape_houses(self, url):
        def get_element_info(element, key):
            return element.find_element(
                By.XPATH, f".//dl/dt[text()='{key}']/preceding-sibling::dd[1]"
            ).text

        logging.info("Search started")

        self.webdriver.get(url)
        pager_xpath = ".//div[@data-testid='pager']//li"
        last_page_number = int(
            self.webdriver.find_element(By.XPATH, f"{pager_xpath}[last()-1]").text
        )
        result = []
        for page_number in range(1, last_page_number + 1):
            logging.info(f"Scrapin page: {page_number} out of {last_page_number}")
            if page_number >= 2:
                self.webdriver.click_when_clickable(
                    By.XPATH,
                    f"{pager_xpath}/a[contains(@aria-label, 'Page {page_number}')]",
                )
            articles = self.webdriver.find_elements(
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

    def detect_form_type(self):
        if self.webdriver.find_element(
            By.NAME, "applicationPackageCompleted"
        ).is_displayed():
            return InterviewForm
        if self.webdriver.find_element(By.NAME, "smoker").is_displayed():
            return SmokerForm
        if self.webdriver.find_element(By.NAME, "income").is_displayed():
            return EasyForm

        raise NotImplementedError("Not implemented form found")

    def send_message(self, form_details, message):
        sleep(3)
        self.webdriver.click_when_clickable(By.XPATH, ".//a[@data-qa='sendButton']")
        sleep(2)
        self.webdriver.find_and_send_key(By.ID, "contactForm-Message", message)
        if self.webdriver.find_element(By.NAME, "moveInDateType").is_displayed():
            form_type = self.detect_form_type()
            self.set_form_filler(form_type)
            self.form_filler.fill_form(form_details)

        self.webdriver.click_when_clickable(
            By.XPATH, ".//button[@data-qa='sendButtonBasic']", time_out=60
        )

        logging.info(f"Message successfully sent")

    def get_detail(self, house):
        logging.info(f"Got the house with address {house['Address']}. Getting details")
        self.webdriver.get(house["link"])
        if self.webdriver.find_elements(By.XPATH, NOT_ACTIVE_XPATH):
            logging.info("Found deactivated house. Deleting it from DB")
            return False

        description_elements = self.webdriver.find_elements(
            By.XPATH,
            ".//div[@id='is24-content']/div[contains(@class, "
            "'contact-box')]/following-sibling::div[1]//div["
            "contains(@class, 'is24-text')]",
        )
        description_texts = " ".join(element.text for element in description_elements)
        title = self.webdriver.find_element(By.ID, "expose-title").text
        owner = self.webdriver.find_element(
            By.XPATH, ".//div[@data-qa='contactName']"
        ).text
        house_detailed = {
            **house,
            "title": title,
            "owner": owner,
            "description": description_texts,
            "rooms": self.webdriver.find_element(
                By.XPATH, ".//div[contains(@class, 'zi-main')]"
            ).text,
        }
        return house_detailed

    def contact_owner(self, owner, address, user_form_details, message):
        logging.info(
            f"Extracted details of house with address {address}. Sending message now to owner {owner}"
        )
        self.send_message(user_form_details, message)
