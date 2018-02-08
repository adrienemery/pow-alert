#! /usr/bin/env python

import os
import sys
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TWILIO_ACCOUNT_SID = os.environ.get("TWILLIO_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILLIO_AUTH_TOKEN")
TO_NUMBER = os.environ.get("TO_NUMBER")
FROM_NUMBER = os.environ.get("FROM_NUMBER")


def send_sms(text):
    # Send text message
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    client.api.account.messages.create(
        to=TO_NUMBER,
        from_=FROM_NUMBER,
        body=text)

