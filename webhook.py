#! /usr/bin/env python


from pow_alert_malc import check_snow, pretify_data
import SQLitedb as sql
from flask import Flask, request
from flask_cors import CORS
from flask.json import jsonify
import notifications
import json
import os

app = Flask(__name__)
CORS(app)


def update(to_num):
    result = check_snow()
    txt_message = pretify_data(result)
    notifications.send_sms(txt_message, to_num)

@app.route('/')
def handler():
    msg = request.args['Body'].lower().strip()
    client_num = request.args['From']
    # when using notifications.send_sms() method, remember that From and To args received are reversed when message sent

    sql.update_database(client_num, msg)

    if msg.lower().strip() == "update":
        update(client_num)
    elif msg == "register":
        txt = f"You will now receive updates in the morning if it snows overnight " \
              f"on the Vancouver local mountains.\n" \
              f"You can stop it at any moment by sending 'unregister' to this number."
        notifications.send_sms(txt, client_num)
    elif msg == "unregister":
        txt = f"You will stop receiving automatic updates. You can always reactivate the service by sending 'register'."
        notifications.send_sms(txt, client_num)
    elif msg == "remove":
        txt = f"Your phone number has been successfully removed from the database."
        notifications.send_sms(txt, client_num)
    elif msg == "information":
        txt = f"Here are the keywords you can use:\n" \
               "'update': you will receive the current status on the mountain.\n\n" \
               "'register': you will be registered for morning texts if fresh snow on the local mountain.\n\n" \
               "'unregister': you will not receive morning texts anymore.\n\n" \
               "'information': lists all available keywords and their effect."
        notifications.send_sms(txt, client_num)
    else:
        txt = f"Sorry buddy, the only keywords accepted are 'update', 'register' and 'unregister'.\n" \
               "If it's your first time using the app, send 'information' for more insight on the keywords effects."
        notifications.send_sms(txt, client_num)

    return ''  # Flask needs a return str

@app.route('/json')
def index():
    result = check_snow()
    return jsonify(result)

@app.route('/github', methods=['POST'])
def github_hook():
    data = json.loads(request.data)
    if data['events'] == 'pull_request':
        os.system("git pull")
        os.system("service pow-alert restart")


if __name__ == "__main__":
    app.run()


