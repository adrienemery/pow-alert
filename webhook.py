#! /usr/bin/env python


from pow_alert_malc import check_snow, pretify_data
import SQLitedb as sql
from flask import Flask, request
from flask_cors import CORS
from flask.json import jsonify
import notifications

app = Flask(__name__)
CORS(app)


def update(to_num):
    result = check_snow()
    txt_message = pretify_data(result)
    notifications.send_sms(txt_message, to_num)

@app.route('/')
def handler():
    msg = request.args['Body']
    client_num = request.args['From']
    # when using notifications.send_sms() method, remember that From and To args received are reversed when message sent

    sql.update_database(client_num, msg.lower())

    if msg.lower().strip() == "update":
        update(client_num)
    elif msg.lower().strip() == "register":
        txt = f"You will now receive updates in the morning if it snows overnight " \
              f"on the Vancouver local mountains.\n" \
              f"You can stop it at any moment by sending 'unregister' to this number."
        notifications.send_sms(txt, client_num)
    elif msg.lower().strip() == "unregister":
        txt = f"You will stop receiving automatic updates. You can always reactivate the service by sending 'register'."
        notifications.send_sms(txt, client_num)
    elif msg.lower().strip() == "remove":
        txt = f"Your phone number has been successfully removed from the database."
        notifications.send_sms(txt, client_num)
    elif msg.lower().strip() == "information":
        txt = f"Here are the keywords you can use:\n" \
               "'update': you will receive the current status on the mountain.\n\n" \
               "'register': you will be registered for morning text if fresh snow on the local mountain.\n\n" \
               "'unregister': you will not receive morning texts anymore.\n\n" \
               "'information': lists all available keywords and their effect."
        notifications.send_sms(txt, client_num)
    else:
        txt = f"Sorry buddy, the only keywords accepted are 'update', 'register', 'unregister'.\n" \
               "Send 'information' if you want more information on the keywords effects."
        notifications.send_sms(txt, client_num)

    return ''  # Flask needs a return str

@app.route('/json')
def index():
    result = check_snow()
    return jsonify(result)


if __name__ == "__main__":
    app.run()


