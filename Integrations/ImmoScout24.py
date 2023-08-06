import undetected_chromedriver as uc
import Scraper
import os
from BaseIntegration import BaseIntegration
import logging
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By


# Configure the logger
logging.basicConfig(level=logging.INFO)


class ImmoScout24(BaseIntegration):
    url = "https://www.immobilienscout24.de/"
    login_xpath = ".//a[text()='Anmelden']"
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]

    def __init__(self):
        super().__init__()
        self.scraper.add_response_checker(self.response_checker)
        self.scraper.add_headers(
            {
                "Host": "www.immobilienscout24.de",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.immobilienscout24.de/meinkonto/dashboard/",
            }
        )

    def response_checker(self, response: Scraper):
        if response.headers.get("Content-Type") == "application/json; charset=utf-8":
            response = self.scraper.request(response.json["full_path"])

        return response

    def login(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        driver = uc.Chrome(headless=False, use_subprocess=False, options=options)
        driver.maximize_window()
        driver.get(self.url)

        sleep(5)
        cookie_button = driver.execute_script(
            """return  document.querySelector('#usercentrics-root').shadowRoot.querySelector("button[data-testid='uc-accept-all-button']")"""
        )
        cookie_button.click()
        sleep(5)
        anmelden_button = driver.find_element(By.XPATH, self.login_xpath)
        anmelden_button.click()
        sleep(2)
        input("Press Enter after solving the reCAPTCHA: ")
        username_input = driver.find_element(By.XPATH, ".//input[@id='username']")
        username_input.send_keys(self.username)
        sleep(1)
        submit = driver.find_element(By.ID, "submit")
        submit.click()
        sleep(3)
        password_input = driver.find_element(By.ID, "password")
        sleep(1)
        password_input.send_keys(self.password)
        sleep(2)
        submit = driver.find_element(By.ID, "loginOrRegistration")
        submit.click()
        sleep(3)
        email_code_list = driver.find_elements(By.XPATH, './/*[@name="answer"]')
        if len(email_code_list) > 0:
            self.do_2fa(driver, email_code_list)

        sleep(3)
        driver.get(self.url)
        driver_cookies = driver.get_cookies()
        page = driver.page_source
        driver.quit()
        for cookie in driver_cookies:
            self.scraper.add_cookies(cookie)

    @staticmethod
    def do_2fa(driver, elements):
        code = input("Give the the from email")
        email_code_input = elements[0]
        email_code_input.send_keys(code)
        sleep(3)
        confirm_button = driver.find_element(By.XPATH, ".//input[@value='Bestätigen']")
        confirm_button.click()

    def start_search(self):
        response = self.scraper.request(
            "https://www.immobilienscout24.de/Suche/de/bayern/muenchen/wohnung-mieten?numberofrooms=1.5-&price=-900.0&pricetype=rentpermonth&enteredFrom=one_step_search"
        )
        print("test")

    def scrape(self):
        self.login()
        self.start_search()
