import os
from dataclasses import dataclass


@dataclass
class User:
    _name: str = None
    _surname: str = None
    _age: str = None
    _subject: str = None
    _home_country: str = None
    _experience: str = None
    _university: str = None
    _job: str = None
    _phone: str = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def surname(self):
        return self._surname

    @surname.setter
    def surname(self, value):
        self._surname = value

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = value

    @property
    def experience(self):
        return self._experience

    @experience.setter
    def experience(self, value):
        self._experience = value

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def university(self):
        return self._university

    @university.setter
    def university(self, value):
        self._university = value

    @property
    def job(self):
        return self._job

    @job.setter
    def job(self, value):
        self._job = value

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        self._phone = value

    @classmethod
    def from_env(cls):
        name = os.environ.get("NAME", None)
        surname = os.environ.get("SURNAME", None)
        age = os.environ.get("AGE", None)
        subject = os.environ.get("SUBJECT", None)
        home_country = os.environ.get("COUNTRY", None)
        experience = os.environ.get("EXPERIENCE", None)
        university = os.environ.get("UNIVERSITY", None)
        job = os.environ.get("JOB", None)
        phone = os.environ.get("PHONE", None)

        return cls(
            name,
            surname,
            age,
            subject,
            home_country,
            experience,
            university,
            job,
            phone,
        )

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
            "employmentStatus": "INDEFINITE_PERIOD",
            "rentArrears": "false",
            "insolvencyProcess": "false",
            "smoker": "false",
            "forCommercialPurposes": "false",
        }

    @staticmethod
    def get_email_template():
        return """
    Sehr geehrte %s,
    ich bin %s und %s Jahre alt. Ursprünglich komme ich aus Istanbul, doch die letzten %s Jahre habe ich in 
    München gewohnt. Mein Studium der %s an der %s habe ich vor Kurzem erfolgreich 
    abgeschlossen, und seit nunmehr zwei Wochen arbeite ich als Vollzeit-%s. Ich interessiere mich für 
    Ihre Wohnung!
    Wenn Sie noch weitere Fragen haben oder Interesse daran, mich besser kennenzulernen, stehe ich gerne 
    zur Verfügung.Ich würde mich auf eine Rückmeldung sehr freuen! Meine Handynummer ist: %s

    Herzliche Grüße,
    %s
    """
