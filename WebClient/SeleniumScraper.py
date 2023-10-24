import logging
from time import sleep
import undetected_chromedriver as uc
from lxml import html
from undetected_chromedriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ScraperFactory import ScraperFactory


class SeleniumScraper(ScraperFactory):
    def __init__(self):
        self.driver: Chrome = None
        self._response_checker = None
        # self.driver.maximize_window()

    def init_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        self.driver = uc.Chrome(
            headless=False, use_subprocess=False, options=options, version_main=117
        )

    def close(self):
        self.driver.close()

    def add_response_checker(self, func):
        self._response_checker = func

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
    def solve_bot_detection():
        input("Please press enter after you solve recaptcha.")
        sleep(4)

    def click_element(self, element):
        element.click()
        sleep(3)
        self._response_checker(self.driver)

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
        self._response_checker(self.driver)

    def execute_script(self, script):
        return self.driver.execute_script(script)

    def handle_cookies(self):
        cookie_button = self.driver.execute_script(
            """return  document.querySelector('#usercentrics-root').shadowRoot.querySelector("button[data-testid='uc-accept-all-button']")"""
        )
        self.click_element(cookie_button)

    @staticmethod
    def take_screenshot(element):
        path = "../ML/image.png"
        element.screenshot(path)
        logging.info(f"Saved image as image.png")
        return path
