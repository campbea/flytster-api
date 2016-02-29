import xml.etree.ElementTree as ET
import requests

from django.conf import settings

from jinja2 import Environment, PackageLoader

# WILL FINISH THIS SECTION ONCE I GET SABRE CREDENTIALS

def start_sabre_session():
    """
    Sends xml-formatted SOAP request to start Sabre session
    """
    env = Environment(loader=PackageLoader('sabre', 'templates'))

    context = {
        "EMAIL": settings.EMAIL_HOST_USER,
        "USERNAME": settings.SABRE_USERNAME,
        "PASSWORD": settings.SABRE_PASSWORD,
        "PCC": "PPC",
        "DOMAIN": "DEFAULT"
    }

    template = env.get_template('start_session.xml')
    soap_req = template.render(context)

    headers = {'content-type': 'text/xml'}
    response = requests.post(settings.SABRE_TESTING_URL, data=soap_req, headers=headers)
    print(response.status_code)
    print(response.content)
    # will get sabre token
    token = response
    return token

def close_sabre_session(token):
    """
    Sends xml-formatted SOAP request to close Sabre session
    Eventually will implement a refresh session to stop token timeout after 15 min
    """
    env = Environment(loader=PackageLoader('sabre', 'templates'))

    context = {
        "PCC": "PPC",
        "EMAIL": settings.EMAIL_HOST_USER,
        "TOKEN": token
    }

    template = env.get_template('close_session.xml')
    soap_req = template.render(context)

    headers = {'content-type': 'text/xml'}
    response = requests.post(settings.SABRE_TESTING_URL, data=soap_req, headers=headers)
    print(response.status_code)
    print(response.content)


def check_air_availability(token, trip):
    """
    Sends xml-formatted SOAP request to check trip availability with Sabre
    """
    env = Environment(loader=PackageLoader('sabre', 'templates'))

    context = {
        "PCC": "PPC",
        "EMAIL": settings.EMAIL_HOST_USER,
        "TOKEN": token,
        "TRIP": trip
    }

    template = env.get_template('check_air_availability.xml')
    soap_req = template.render(context)
    print(soap_req)

    headers = {'content-type': 'text/xml'}
    response = requests.post(settings.SABRE_TESTING_URL, data=soap_req, headers=headers)
    import pprint
    pprint.pprint(response.status_code)
    pprint.pprint(response.content)


def book_air_segment(token, trip):
    """
    Sends xml-formatted SOAP request to book a flight with Sabre
    """
    env = Environment(loader=PackageLoader('sabre', 'templates'))

    context = {
        "PCC": "PPC",
        "EMAIL": settings.EMAIL_HOST_USER,
        "TOKEN": token,
        "TRIP": trip
    }

    template = env.get_template('book_air_segment.xml')
    soap_req = template.render(context)
    print(soap_req)

    headers = {'content-type': 'text/xml'}
    response = requests.post(settings.SABRE_TESTING_URL, data=soap_req, headers=headers)
    print(response.status_code)
    print(response.content)
