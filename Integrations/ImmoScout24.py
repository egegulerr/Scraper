import json

import httpx
import undetected_chromedriver as uc
from lxml import html

import Scraper
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
    client = httpx.Client(http2=True, verify=False, follow_redirects=True)
    username = "mbcguler@gmail.com"
    password = "Fbguler45!!"

    def __init__(self):
        super().__init__()
        self.scraper.add_response_checker(self.response_checker)
        self.scraper.add_headers(
            {
                "Host": "www.immobilienscout24.de",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-GB,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.immobilienscout24.de/",
            }
        )

    def response_checker(self, response: Scraper):
        if response.headers.get("Content-Type") == "application/json; charset=utf-8":
            response = self.scraper.request(response.json["full_path"])

        return response

    def login(self, response):
        cookies = self.get_cookie_with_driver()

        # add cookies to the httpx client's cookie jar
        for cookie in cookies:
            self.client.cookies.set(cookie["name"], cookie["value"])

        response = self.client.get(
            url="https://sso.immobilienscout24.de/sso/login?appName=is24main&source=headericon&sso_return=https://www.immobilienscout24.de/sso/login.go?source=headericon&returnUrl=/geschlossenerbereich/start.html?source%3Dheadericon",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-GB,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.immobilienscout24.de/",
                "DNT": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-site",
                "Host": "sso.immobilienscout24.de",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        tree = html.fromstring(response.content.decode("utf-8"))
        tokenInput = tree.xpath(".//input[contains(@id, 'token')]")[0]
        token_name, token_value = tokenInput.attrib["name"], tokenInput.attrib["value"]
        payload = {"username": self.username, token_name: token_value}

        response = self.client.post(
            "https://sso.immobilienscout24.de/sso/login?appName=is24main&source=headericon&sso_return=https://www.immobilienscout24.de/sso/login.go?source=headericon&returnUrl=/geschlossenerbereich/start.html?source%3Dheadericon",
            data=payload,
        )
        tree = html.fromstring(response.text)
        form = tree.xpath(".//form[@id='loginForm']")[0]
        payload = dict(form.form_values())
        payload["password"] = self.password
        response1 = self.client.post(
            url=response.url,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-GB,en;q=0.5",
                "Host": "sso.immobilienscout24.de",
                "Origin": "https://sso.immobilienscout24.de",
                "Referer": "https://sso.immobilienscout24.de/",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        state_token = response1.url.params.get("stateToken")
        deneme = self.client.post(
            url="https://login.immobilienscout24.de/api/v1/authn/factors/emf8fmcdnvJdnrSDq417/verify/resend",
            data=json.dumps({"stateToken": state_token}),
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "de",
                "Host": "login.immobilienscout24.de",
                "Origin": "https://login.immobilienscout24.de",
                "Sec-Ch-Ua-Platform": "Windows",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Accept": "application/json",
                "X-Okta-User-Agent-Extended": "okta-auth-js/7.0.1 okta-signin-widget-7.8.1",
            },
            cookies={"oktaStateToken": state_token},
        )
        email_code = input("Give the 2fa code")
        url = deneme.json()["_links"]["next"]["href"]
        response = self.client.post(
            url=f"{url}?rememberDevice=false",
            data=json.dumps({"passCode": email_code, "stateToken": state_token}),
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "de",
                "Host": "login.immobilienscout24.de",
                "Origin": "https://login.immobilienscout24.de",
                "Sec-Ch-Ua-Platform": "Windows",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Accept": "application/json",
                "X-Okta-User-Agent-Extended": "okta-auth-js/7.0.1 okta-signin-widget-7.8.1",
            },
            cookies={"oktaStateToken": state_token},
        )
        session_token = response.json()["sessionToken"]
        client_id = response1.url.params.get("client_id")
        state = response1.url.params.get("state")
        redirect_url = response1.url.params.get("redirect_uri")
        url = (
            f"https://login.immobilienscout24.de/oauth2/aus1227au6oBg6hGH417/v1/authorize?client_id=is24-sso-auth-de"
            f"&nonce=y6Kyk7w8WtQ6vLhqbQqq6awfndxsbvxQKg52ZIRLWOsTODRYoiuzFI29F9GQFiaC&redirect_uri={redirect_url}&response_type=code&sessionToken={session_token}&state="
            f"{state}&scope=openid"
        )
        url2 = (
            "https://login.immobilienscout24.de/oauth2/aus1227au6oBg6hGH417/v1/authorize?client_id=is24-sso-auth"
            "-de&nonce=y6Kyk7w8WtQ6vLhqbQqq6awfndxsbvxQKg52ZIRLWOsTODRYoiuzFI29F9GQFiaC&redirect_uri=https://sso"
            ".immobilienscout24.de/oidc/callback&response_type=code&sessionToken=20111Z_qYPFoL1"
            "--3Lf85YlA_eju9tay1w49TlrHs1AvCKjvA2mkVf-&state"
            "=eyJyZWRpcmVjdFVybCI6Imh0dHBzOi8vd3d3LmltbW9iaWxpZW5zY291dDI0LmRlL3Nzby9sb2dpbi5nbz9zb3VyY2VcdTAwM2RoZWFkZXJpY29uXHUwMDI2cmV0dXJuVXJsXHUwMDNkL2dlc2NobG9zc2VuZXJiZXJlaWNoL3N0YXJ0Lmh0bWw_c291cmNlJTNEaGVhZGVyaWNvbiIsImNvb2tpZVZhbHVlIjoiYWFmZWFlMDQtN2IzYS00OGZkLWI2N2ItMTE1YjUzNjk0MzkyIiwicmVwb3J0Qm9keSI6eyJkZXZpY2VJZEFuZFNlY3JldCI6eyJkZXZpY2VJZCI6ImUwMTNlMjdiLTFlY2UtNGJiMi1iNTAwLTEyMmY1ZTdjMDcwZiIsImRldmljZVNlY3JldCI6IjVlZWZmMmVkLTE1Y2YtNDUxNS04ZjU2LTEzMjg2NjJhOTExOCIsImVuZm9yY2VIdHRwcyI6ZmFsc2V9LCJhcHBOYW1lIjoiaXMyNG1haW4iLCJyZXBvcnRpbmdTb3VyY2UiOiJoZWFkZXJpY29uIiwiaXNSZW1lbWJlck1lIjp0cnVlLCJpc1JlYXV0aGVudGljYXRpb24iOmZhbHNlfX0&scope=openid"
        )
        response12 = self.client.get(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-GB,en;q=0.5",
                "Upgrade-Insecure-Requests": "1",
                "Host": "login.immobilienscout24.de",
            },
            cookies={"oktaStateToken": state_token},
        )

        print("ege")

    def get_cookie_with_driver(self):
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
        sleep(3)
        driver_cookies = driver.get_cookies()
        driver.quit()

        return driver_cookies

    def scrape(self):
        response = self.scraper.request(self.url)
        self.login(response)
        # driver = webdriver.Edge()
        # driver.get("https://www.google.com/")
        # print("ege")
