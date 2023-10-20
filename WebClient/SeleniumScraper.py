from selenium import webdriver
from time import sleep
from lxml import html
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .ScraperFactory import ScraperFactory


class SeleniumScraper(ScraperFactory):
    def __init__(self, web_driver_options=None):
        options = uc.ChromeOptions()
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        if web_driver_options:
            for arg in web_driver_options:
                options.add_argument(arg)
        self.driver = uc.Chrome(
            headless=False, use_subprocess=False, options=options, version_main=117
        )
        # self.driver.maximize_window()
        self._response_checker = None

    def close(self):
        self.driver.close()

    def add_response_checker(self, function):
        self._response_checker = function

    @staticmethod
    def response_checker_decorator(func):
        def wrapper(self, *args, **kwargs):
            def check():
                if (
                    self._response_checker
                    and self.driver.current_url != "chrome://welcome/"
                ):
                    self._response_checker(html.fromstring(self.driver.page_source))

            check()
            response = func(self, *args, **kwargs)
            sleep(4)
            check()
            return response

        return wrapper

    @response_checker_decorator
    def get(self, url):
        self.driver.get(url)

    @property
    def content(self):
        return self.driver.page_source

    @staticmethod
    def solve_recaptcha():
        input("Please press enter after you solve recaptcha.")
        sleep(4)

    def click_element(self, element):
        element.click()
        sleep(3)
        self._response_checker(html.fromstring(self.driver.page_source))

    def find_and_click_element(self, method, selector):
        element = self.driver.find_element(method, selector)
        self.click_element(element)

    def find_and_send_key(self, method, selector, key):
        element = self.driver.find_element(method, selector)
        element.clear()
        element.send_keys(key)
        sleep(3)

    def find_elements(self, method, selector):
        return self.driver.find_elements(method, selector)

    def find_element(self, method, selector):
        return self.driver.find_element(method, selector)

    def click_when_clickable(self, method, selector, time_out=5):
        WebDriverWait(self.driver, time_out).until(
            EC.element_to_be_clickable(
                (
                    method,
                    selector,
                )
            )
        ).click()
        sleep(3)
        self._response_checker(html.fromstring(self.driver.page_source))

    def execute_script(self, script):
        return self.driver.execute_script(script)

    def handle_cookies(self):
        cookie_button = self.driver.execute_script(
            """return  document.querySelector('#usercentrics-root').shadowRoot.querySelector("button[data-testid='uc-accept-all-button']")"""
        )
        self.click_element(cookie_button)
