# /usr/bin/env python

import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from datetime import datetime
startTime = datetime.now()

CYPRESS = "Cypress"
WHISTLER = "Whistler - Blackomb"

load_dotenv(find_dotenv())
options = webdriver.ChromeOptions()
options.add_argument("--headless")


class Resort:

    def __init__(self, name, cam_url, info_url):
        self.name = name or "default"
        self.webcam_url = cam_url or "http://"
        self.info_url = info_url or "http://"
        self.webcam_img = None
        self._24hsnow = "???"
        self._12hsnow = "???"

    def update(self):
        if self.name == CYPRESS:
            print("Cypress Update")
            self.webcam_img = urlopen(self.webcam_url).read()
            page = requests.get(self.info_url)
            soup = BeautifulSoup(page.content, 'html.parser')

            all_div = soup.find_all('div', class_='weather-item clearfix')
            for div in all_div:
                if "24 hr Snow" in div.text:
                    el = div.find('span', class_='numbers')
                    self._24hsnow = el.text

        if self.name == WHISTLER:
            print("Whistler Update")
            # solution with Selenium
            # options = webdriver.ChromeOptions()
            # options.add_argument("--headless")
            # browser = webdriver.Chrome(chrome_options=options)
            # browser.get(self.info_url)
            # sleep(4)
            # self._12hsnow = browser.find_element_by_id('Last12Hours').text
            # self._24hsnow = browser.find_element_by_id('Last24Hours').text
            # browser.quit()

            # Solution with other url and No selenium
            info_url = "https://www.pembertonvalleylodge.com/pemberton/snow-conditions/"
            page = requests.get(info_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            all_div = soup.find_all('div', id='conditions')
            for el in all_div:
                tab_snowfall = el.find("table", {"class": "tomtable"})
            tab = []
            for row in tab_snowfall.find_all('tr'):
                for col in row.find_all('td'):
                    if col.text:
                        tab.append(col.text)
            self._12hsnow = (tab[5].split(' '))[0]
            self._24hsnow = (tab[6].split(' '))[0]

    @property
    def info(self):
        self.update()
        print(self.name+" report:")
        print(self._12hsnow+" overnight")
        print(self._24hsnow + " last 24h")
        print("*********")


Cypress = Resort(name=CYPRESS,
                 cam_url="http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768",
                 info_url="http://www.cypressmountain.com/downhill-conditions/")

Whistler = Resort(name=WHISTLER,
                  cam_url="http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768",
                  info_url="https://www.whistlerblackcomb.com/mountain-info/snow-report")

Cypress.info
Whistler.info

print(datetime.now() - startTime)

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
