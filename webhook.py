#! /usr/bin/env python


from pow_alert_malc import check_snow, pretify_data
from flask import Flask, request
from flask_cors import CORS
from flask.json import jsonify
import notifications

app = Flask(__name__)
CORS(app)


def update():
    result = check_snow()
    txt_message = pretify_data(result)
    notifications.send_sms(txt_message)

@app.route('/')
def handler():
    msg = request.args['Body']
    if msg.lower() == "update":
        update()
    else:
        notifications.send_sms("Sorry buddy")

@app.route('/json')
def index():
    result = check_snow()
    return jsonify(result)


if __name__ == "__main__":
    app.run()


