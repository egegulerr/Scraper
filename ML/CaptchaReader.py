import logging

from google.cloud import vision


class CaptchaReader:
    @staticmethod
    def detect_text(path):
        client = vision.ImageAnnotatorClient()

        with open(path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        if response.error.message:
            raise Exception(
                "{} Error occured while reading captcha iamge: ".format(
                    response.error.message
                )
            )

        for text in texts:
            print(f'\n" Captcha text: {text.description}"')
            return text.description
