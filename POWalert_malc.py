# /usr/bin/env python

import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup

load_dotenv(find_dotenv())


class Resort:

    def __init__(self, name, cam_url, info_url):
        self.name = name or "default"
        self.webcam_url = cam_url or "http://"
        self.info_url = info_url or "http://"
        self.webcam_img = None
        self._24hsnow = None
        self._12hsnow = None

    def update(self):
        self.webcam_img = urlopen(img_url).read()
        page = requests.get(info_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        all_div = soup.find_all('div', class_='weather-item clearfix')
        for div in all_div:
            if "24 hr Snow" in div.text:
                el = div.find('span', class_='numbers')
                self._24hsnow = el.text


Cypress = Resort(name="Cypress",
                 cam_url="http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768",
                 info_url="http://www.cypressmountain.com/downhill-conditions/")


#with open('test.jpg', 'wb') as file:
#    file.write(cypress)



#
# # Find these values at https://twilio.com/user/account
# account_sid = os.environ.get("account_sid")
# auth_token = os.environ.get("auth_token")
#
# client = Client(account_sid, auth_token)
#
# client.api.account.messages.create(
#     to=os.environ.get("Malcolm_phone_nbr"),
#     from_=os.environ.get("Twilio_phone_nbr"),
#     body="attempt with dotenv")
