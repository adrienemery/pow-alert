# /usr/bin/env python

import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
from urllib.request import urlopen
import requests
import re
import json
from bs4 import BeautifulSoup

load_dotenv(find_dotenv())

CYPRESS = "Cypress"
WHISTLER = "Whistler - Blackomb"
TWILIO_ACCOUNT_SID = os.environ.get("TWILLIO_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILLIO_AUTH_TOKEN")
MALCOLM_PHONE_NUMBER = os.environ.get("TO_NUMBER"),
TWILIO_PHONE_NUMBER = os.environ.get("FROM_NUMBER")



class Resort:

    def __init__(self, name, cam_url=None, info_url=None):
        self.name = name or "default"
        self.webcam_url = cam_url
        self.info_url = info_url
        self.webcam_img = None
        self._24hsnow = "???"
        self._12hsnow = "???"

    def update(self):
        if self.webcam_url:
            self.webcam_img = urlopen(self.webcam_url).read()

        page = requests.get(self.info_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        if self.name == CYPRESS:
            all_div = soup.find_all('div', class_='weather-item clearfix')
            for div in all_div:
                if "24 hr Snow" in div.text:
                    el = div.find('span', class_='numbers')
                    self._24hsnow = el.text

        if self.name == WHISTLER:
            text_json = re.search('FR.snowReportData = ({.*});', page.text)
            data = json.loads(text_json.groups()[0])
            self._24hsnow = data['TwentyFourHourSnowfall']['Centimeters']
            self._12hsnow = data['OvernightSnowfall']['Centimeters']

    def discard_info(self):
        print(self.name+" report:")
        print(self._12hsnow+" cm overnight")
        print(self._24hsnow + " cm last 24h")
        print("*********")

    @property
    def data(self):
        self.update()
        return self.name + " report:\n" + \
               self._12hsnow + " cm overnight\n" + \
               self._24hsnow + " cm last 24h\n" + \
               "******************\n"


Cypress = Resort(name=CYPRESS,
                 cam_url="http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768",
                 info_url="http://www.cypressmountain.com/downhill-conditions/")

Whistler = Resort(name=WHISTLER,
                  info_url="https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx")

text_message = Cypress.data + Whistler.data


# Send text message
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

client.api.account.messages.create(
    to=MALCOLM_PHONE_NUMBER,
    from_=TWILIO_PHONE_NUMBER,
    body=text_message)
