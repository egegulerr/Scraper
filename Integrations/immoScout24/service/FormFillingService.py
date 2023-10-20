from abc import ABC, abstractmethod
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


class FormFillingStrategy(ABC):
    def __init__(self, webdriver):
        self.webdriver = webdriver

    @abstractmethod
    def fill_form(self, form_details):
        self.select_option("moveInDateType", form_details["moveInDateType"])
        self.select_option("hasPets", form_details["hasPets"])
        self.select_option(
            "employmentRelationship", form_details["employmentRelationship"]
        )

    def select_option(self, select_name, option_value):
        Select(self.webdriver.find_element(By.NAME, select_name)).select_by_value(
            option_value
        )


# TODO find better form names
# TODO Maybe use dependency injection for form_details.
class SmokerForm(FormFillingStrategy):
    def fill_form(self, form_details):
        super().fill_form(form_details)
        self.select_option("employmentStatus", form_details["employmentStatus"])
        self.select_option("rentArrears", form_details["rentArrears"])
        self.select_option("insolvencyProcess", form_details["insolvencyProcess"])
        self.select_option("smoker", form_details["smoker"])
        self.select_option(
            "forCommercialPurposes", form_details["forCommercialPurposes"]
        )
        pass


class InterviewForm(FormFillingStrategy):
    def fill_form(self, form_details):
        super().fill_form(form_details)
        self.select_option("numberOfPersons", form_details["numberOfPersons"])
        self.select_option("income", form_details["income"])
        self.select_option(
            "applicationPackageCompleted",
            form_details["applicationPackageCompleted"],
        )


class EasyForm(FormFillingStrategy):
    def fill_form(self, form_details):
        super().fill_form(form_details)
        self.select_option("numberOfPersons", form_details["numberOfPersons"])
        self.select_option("income", form_details["income"])


class FormFiller:
    def __init__(self, strategy: FormFillingStrategy):
        self.strategy = strategy

    def fill_form(self, form_details):
        self.strategy.fill_form(form_details)
