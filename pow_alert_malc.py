#! /usr/bin/env python

import sys
from skimage import io
import requests
import re
import json
from bs4 import BeautifulSoup
import notifications
import parse_img
from resort_names import *

resort_names = [CYPRESS, WHISTLER]

try:
    PLOT_DEBUG = sys.argv[1]
except IndexError:
    PLOT_DEBUG = False


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
            self.webcam_img = io.imread(self.webcam_url)
            self._12hsnow = parse_img.read_height(image=self.webcam_img,
                                                  debug_option=PLOT_DEBUG,
                                                  resort=self.name)
        page = requests.get(self.info_url)
        handler_fnc = getattr(self, f'update_{self.name}')
        return handler_fnc(page)


    def update_whistler(self, page):
        text_json = re.search('FR.snowReportData = ({.*});', page.text)
        data = json.loads(text_json.groups()[0])
        self._24hsnow = data['TwentyFourHourSnowfall']['Centimeters']
        self._12hsnow = data['OvernightSnowfall']['Centimeters']

    def update_cypress(self, page):
        soup = BeautifulSoup(page.content, 'html.parser')
        all_div = soup.find_all('div', class_='weather-item clearfix')
        for div in all_div:
            if "24 hr Snow" in div.text:
                el = div.find('span', class_='numbers')
                self._24hsnow = el.text.split(' ')[0]


    def display_info(self):
        print(f"{self.name.tittle()} report:")
        print(f"{self._12hsnow} cm overnight")
        print(f"{self._24hsnow} cm last 24h")
        print("******************")

    @property
    def data(self):
        self.update()
        return {'name':self.name, '12':self._12hsnow, '24':self._24hsnow}


resort_dict = {
    CYPRESS: Resort(name=CYPRESS,
                    cam_url="http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768",
                    info_url="http://www.cypressmountain.com/downhill-conditions/"),

    WHISTLER: Resort(name=WHISTLER,
                     info_url="https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx")
}


def check_snow(resort_list_names=None):
    names = resort_list_names or resort_dict.keys()
    result = []
    for name in names:
        result.append(resort_dict[name].data)
    return result


def pretify_data(data):
    txt = "**Snow Report**"
    for resort in data:
        txt = f"{txt} {resort['name'].title()}:\n" \
              f"{resort['12']}cm last 12h\n" \
              f"{resort['24']}cm last 12h\n" \
              "******************"
    return txt

if __name__ == "__main__":
    txt_message = ""
    for resort in resort_dict.values():
        txt_message = txt_message + resort.data
        if resort.name == CYPRESS and int(resort._12hsnow) > 0:
            io.imsave("test_Cypress.png", resort.webcam_img)

    notifications.send_sms(txt_message)


