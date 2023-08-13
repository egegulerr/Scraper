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
    login_xpath = ".//a[text()='Anmelden']"
    captcha_xpath = (
        ".//div[@class='main__captcha']//p[contains(text(), 'Nachdem du das unten stehende CAPTCHA "
        "bestätigt hast')]"
    )
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]

    def __init__(self, use_selenium=False, webdriver_options=None):
        super().__init__(use_selenium, webdriver_options)

    def setup(self):
        self.scraper.add_response_checker(self.response_checker)

    def response_checker(self, response_body):
        if response_body.xpath(self.captcha_xpath):
            logging.info("Captcha showed up. Solving it")
            self.scraper.solve_recaptcha()

    def login(self):
        self.scraper.get(self.url)
        cookie_button = self.scraper.execute_script(
            """return  document.querySelector('#usercentrics-root').shadowRoot.querySelector("button[data-testid='uc-accept-all-button']")"""
        )
        cookie_button.click()
        sleep(5)
        self.scraper.find_and_click_element(By.XPATH, self.login_xpath)
        self.scraper.find_and_send_key(
            By.XPATH, ".//input[@id='username']", self.username
        )
        self.scraper.find_and_click_element(By.ID, "submit")
        self.scraper.find_and_send_key(By.ID, "password", self.password)
        self.scraper.find_and_click_element(By.ID, "loginOrRegistration")
        email_code_list = self.scraper.find_elements(By.XPATH, './/*[@name="answer"]')
        if len(email_code_list) == 1:
            self.do_2fa(email_code_list[0])

        self.scraper.get(self.url)

    def do_2fa(self, input_field):
        code = input("Give the 2FA code from the from email")
        input_field.send_keys(code)
        sleep(3)
        self.scraper.find_and_click_element(By.XPATH, ".//input[@value='Bestätigen']")

    def get_home_links(self):
        url = urljoin(
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
        self.scraper.get(url)
        pager_xpath = ".//div[@data-testid='pager']//li"
        last_page_number = int(
            self.scraper.find_element(By.XPATH, f"{pager_xpath}[last()-1]").text
        )
        item_links = []
        for page_number in range(1, last_page_number + 1):
            if page_number >= 2:
                self.scraper.click_when_clickable(
                    By.XPATH,
                    f"{pager_xpath}/a[contains(@aria-label, 'Page {page_number}')]",
                )
            item_link_elements = self.scraper.find_elements(
                By.XPATH,
                ".//ul[@id='resultListItems']/li[@data-id]/article/div/div[contains(@class, "
                "'result-list-entry__data-container')]/div[contains(@class, 'result-list-entry__data')]/a",
            )
            item_links.extend(
                [link.get_attribute("href") for link in item_link_elements]
            )
        return item_links

    def get_home_detail_page(self, links):
        for link in links:
            self.scraper.get(link)

    def scrape(self):
        self.login()
        links = self.get_home_links()
        self.get_home_detail_page(links)
        print(links)
