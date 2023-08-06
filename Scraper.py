import requests as re
import json
from lxml import html
from abc import ABC, abstractmethod


class Scraper(ABC):
    _instance = None

    def __init__(self, response=None, response_checker=None, session=None):
        self._response_checker = response_checker
        self._response = response
        if session is None:
            self._session = re.Session()
        else:
            self._session = session

    def add_response_checker(self, f):
        self._response_checker = f

    def add_cookies(self, cookie):
        self._session.cookies.set(cookie["name"], cookie["value"])

    def add_headers(self, headers):
        self._session.headers.update(headers)

    def set_response(self, response):
        self._response = response

    def request(self, url, data=None, headers=None, method=None):
        if method is None:
            method = "GET"

        response_not_checked = Scraper(
            response=self._session.request(
                url=url, data=data, headers=headers, method=method, verify=False
            ),
            session=self._session,
            response_checker=self._response_checker,
        )

        response = self._response_checker(response_not_checked)
        return response

    @property
    def body(self):
        return (
            self._response
            if isinstance(self._response, str)
            else self._response.content.decode("utf-8")
        )

    @property
    def status_code(self):
        return self._response.status_code

    @property
    def headers(self):
        return self._response.headers

    @property
    def json(self):
        return json.loads(self.body.decode())

    @property
    def xpath(self):
        return html.fromstring(self.body)

    @property
    def cookies(self):
        return self._session.cookies

    def find(self, param):
        return self.xpath.xpath(param)
