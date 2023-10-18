import os


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
        appeal = f"{gender} {name}"
        if appeal.strip() is None or appeal.strip() == ".":
            appeal = "Damen und Herren"
        return f"""
    Sehr geehrte {appeal},
    ich bin {User.name} und {User.age} Jahre alt. Ursprünglich komme ich aus Istanbul, doch die letzten {User.experience} Jahre habe ich in 
München gewohnt. Mein Studium der {User.subject} an der {User.university} habe ich vor Kurzem erfolgreich 
abgeschlossen, und seit nunmehr zwei Wochen arbeite ich als Vollzeit-{User.job}. Ich interessiere mich für 
Ihre Wohnung!
    Wenn Sie noch weitere Fragen haben oder Interesse daran, mich besser kennenzulernen, stehe ich gerne 
zur Verfügung.Ich würde mich auf eine Rückmeldung sehr freuen! Meine Handynummer ist: {User.phone}

Herzliche Grüße,
{User.name} 
        """
