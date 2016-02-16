import urllib
import requests


def check_recaptcha(response, secretkey):
    try:
        resp = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": secretkey,
                "response": response
            }
        ).json()
        if resp['success']:
            return True
        else:
            return False
    except Exception as e:
        return False
