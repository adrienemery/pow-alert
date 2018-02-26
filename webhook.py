#! /usr/bin/env python


from pow_alert_malc import check_snow, pretify_data
from flask import Flask, request
from flask_cors import CORS
from flask.json import jsonify
import notifications

app = Flask(__name__)
CORS(app)


def update(to_num, twilio_num):
    result = check_snow()
    txt_message = pretify_data(result)
    notifications.send_sms(txt_message, to_num, twilio_num)

@app.route('/')
def handler():
    msg = request.args['Body']
    num = request.args['From']
    twilio_num = request.args['To']
    # when using notifications.send_sms() method, remember that From and To args received are reversed when message sent

    if msg.lower() == "update":
        update(num, twilio_num)
    else:
        notifications.send_sms("Sorry buddy", num, twilio_num)

    return ''  # Flask needs a return str

@app.route('/json')
def index():
    result = check_snow()
    return jsonify(result)


if __name__ == "__main__":
    app.run()


