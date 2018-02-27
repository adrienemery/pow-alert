#! /usr/bin/env python

import os
import sys
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TWILIO_ACCOUNT_SID = os.environ.get("TWILLIO_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILLIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")


def send_sms(text, to_num):
    # Send text message
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    client.api.account.messages.create(
        to=to_num,
        from_=TWILIO_NUMBER,
        body=text)

