# /usr/bin/env python

import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
from urllib.request import urlopen
import requests
import re
import json
from bs4 import BeautifulSoup


CYPRESS = "Cypress"
WHISTLER = "Whistler - Blackomb"

load_dotenv(find_dotenv())


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

text = Cypress.data + Whistler.data

account_sid = os.environ.get("account_sid")
auth_token = os.environ.get("auth_token")

client = Client(account_sid, auth_token)

client.api.account.messages.create(
    to=os.environ.get("Malcolm_phone_nbr"),
    from_=os.environ.get("Twilio_phone_nbr"),
    body=text)
