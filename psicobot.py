import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)

v_token = process.env.FB_VERIFY_TOKEN
a_token = process.env.FB_ACCESS_TOKEN

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == v_token:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event['sender']['id']        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event['recipient']['id']  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event['message']['text']  # the message's text

                    decideMessage(sender_id, message_text)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["postback"]["payload"]

                    send_message(sender_id, message_text)

    return "ok", 200

def decideMessage(sender_id, message_text):

    text = message_text.lower()

    if "start" in text:
        sendButtonMessage(sender, "¿Que quieres hacer?", [["Empezar a chatear", "chatear"], ["Ir a la pagina web", "web"]])

    elif "chatear" in text:
        sendImageMessage(sender, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkgQAxIYGfodDctizYg_auYhrJO4Jlcy1tGQbvNy9Brp-ZIpNXNQ")

    else:
        sendText(sender, "Disculpa, no entiendo lo que dices")

def sendButtonMessage(sender_id, text):
    message_data = {
        "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":text,
                "buttons":[
                    {
                        "type":"postback",
                        "title":"Si",
                        "payload":"si"
                    },
                    {
                        "type":"postback",
                        "title":"No",
                        "payload":"no"
                    }
                ]
            }
        }
    }

    sendRequest(sender_id, message_data)

def sendImageMessage(sender_id, URL):

    message_data = {
        "attachment":{
            "type":"image",
            "payload":{
                "url":imageURL
            }
        }
    }

    sendRequest(sender_id, message_data)

def sendText(recipient_id, text):
    #log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    
    message_data = {"text":text}

    sendRequest(recipient_id, message_data)

def sendRequest(recipient_id, text):
    params = {
        "access_token": a_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": text
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log("Eror :c")
        log(r.status_code)
        log(r.text)

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)