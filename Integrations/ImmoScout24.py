import os
from BaseIntegration import BaseIntegration
import logging
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from urllib.parse import urljoin, urlencode
from Repository.ImmoScoutRepository import ImmoScoutDB

logging.basicConfig(level=logging.INFO)


class User:
    name = os.environ["NAME"]
    surname = os.environ["SURNAME"]
    age = os.environ["AGE"]
    subject = os.environ["SUBJECT"]
    home_country = os.environ["COUNTRY"]
    experience = os.environ["EXPERIENCE"]
    university = os.environ["UNIVERSITY"]
    job = os.environ["JOB"]
    phone = os.environ["PHONE"]

    @staticmethod
    def get_all_user_details():
        # TODO Maybe fetch datas from database ?
        return {
            "house": User.get_form_details(),
            "search": User.get_search_details(),
        }

    @staticmethod
    def get_search_details():
        return {
            "shape": "b2l4ZEhfcGRlQXZtRGN5QWZkQF9oQXpsQGdxRXNHX21FX3RDcX5HaXdCYXtAdWJDaUN9aEJkd0J5dEFweFVsbUpqX0E.",
            "numberofrooms": "1.0-",
            "price": "-1000.0",
            "exclusioncriteria": "swapflat",
            "pricetype": "calculatedtotalrent",
            "enteredFrom": "result_list#",
        }

    @staticmethod
    def get_form_details():
        return {
            "moveInDateType": "FLEXIBLE",
            "numberOfPersons": "ONE_PERSON",
            "hasPets": "false",
            "employmentRelationship": "WORKER",
            "income": "OVER_2000_UPTO_3000",
            "applicationPackageCompleted": "true",
        }

    @staticmethod
    def get_email_template(gender, name):
        # TODO Maybe storing email with json or creating class for E-Mail could be a good idea
        return f"""
            Sehr geehrte {gender} {name},
    ich bin {User.name} und {User.age} Jahre alt. Ursprünglich komme ich aus Istanbul, doch die letzten {User.experience} Jahre habe ich in 
München gewohnt. Mein Studium der {User.subject} an der {User.university} habe ich vor Kurzem erfolgreich 
abgeschlossen, und seit nunmehr zwei Wochen arbeite ich als Vollzeit-{User.job}. Ich interessiere mich für 
Ihre Wohnung!
    Wenn Sie noch weitere Fragen haben oder Interesse daran, mich besser kennenzulernen, stehe ich gerne 
zur Verfügung.Ich würde mich auf eine Rückmeldung sehr freuen! Meine Handynummer ist: {User.phone}

Herzliche Grüße,
{User.name} 
        """


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
                By.XPATH, ".//ul[@id='resultListItems']/li[@data-id]/article"
            )

            for article in articles:
                isPremiumRequired = "paywall-listing" in article.get_attribute("class")
                # TODO need to implement premium houses
                if isPremiumRequired:
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

    def get_house_details(self, house_info):
        logging.info("Got the house information. Getting details")
        self.scraper.get(house_info["link"])
        # TODO Maybe dont need to scrape with driver. IS24 File could be used ?

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
        house_info.update(
            {
                "title": title,
                "owner": owner,
                "desccription": decription_texts,
                "Rooms": self.scraper.find_element(
                    By.XPATH, ".//div[contains(@class, 'zi-main')]"
                ).text,
            }
        )
        return house_info

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

    def scrape(self):
        try:
            self.login()
            user_search_details = User.get_search_details()
            url = self.get_search_url(user_search_details)
            houses = self.get_general_home_info(url)
            # TODO Maybe dont need connect function here ?
            self.db.connect()
            self.db.insert_founded_houses(houses)
            for house in houses:
                house_detailed = self.get_house_details(house)
                user_details = User.get_form_details()
                try:
                    self.send_message(
                        house_detailed["title"], house_detailed["owner"], user_details
                    )

                except Exception as e:
                    logging.error(f"An error occured while sending the message: {e}")
        except:
            self.db.close()
