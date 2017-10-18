import os, sys
from flask import Flask, request
import json
import requests
#from utils import wit_response
from pymessenger import Bot
from os import environ

app = Flask(__name__)

#v_token = environ.get('FB_VERIFY_TOKEN')
#a_token = environ.get('FB_ACCESS_TOKEN')

v_token = "blondiebytes"
a_token = "EAADZBqZBZC8rAIBAMFr6AfGjK6aml9o5N2l1FWyQwm4as7ZCZAKyAIehLplXAH6xUamUX2LBHfG97SHtAe9yeSR0qCb2an6GcFbmrbflkTZCYBkqf64ZALSma3xegly5MZAYWdUwZCY7MSTPXRovZAUVEicAjxHq4wXU4u0GtboM0LsAZDZD"

bot = Bot(a_token)

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
    log(data)
    log("\n")

    if data['object'] == 'page':
        for entry in data['entry']:
            if entry.get("messaging"):
                for messaging_event in entry['messaging']:

                    sender_id = messaging_event["sender"]["id"] # FB ID of the person sending you the message
                    recipient_id = messaging_event['recipient']['id'] # Chatbot ID

                    # Text Message
                    if messaging_event.get("message"):  # someone sent us a message
                        if 'text' in messaging_event['message']:
                            message_text = messaging_event['message']['text']  # the message's text
                        else:
                            message_text = "no text"
                        decideMessage(sender_id, message_text)

                    # Button Answer
                    elif messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                        message_text = messaging_event["postback"]["payload"] # Button answer text
                        decideMessage(sender_id, message_text)

                    elif messaging_event.get("delivery"):  # delivery confirmation
                        pass

                    elif messaging_event.get("optin"):  # optin confirmation
                        pass

    return "ok", 200

def decideMessage(sender_id, message_text):

    text = message_text.lower()

    if "start" in text:

        buttons = [
                    {
                        "type":"postback",
                        "title": "Empezar a chatear",
                        "payload": "chatear"
                    },
                    {
                        "type":"postback",
                        "title": "Ir a la pagina web",
                        "payload": "web"
                    }
        ]

        bot.send_button_message(sender_id, "¿Que quieres hacer?", buttons)

    elif "chatear" in text:
        bot.send_text_message(sender_id, ":D")

    else:
        bot.send_text_message(sender_id, "Disculpa, no entiendo lo que dices")

def sendButtonMessage(sender_id, text, options):
    message_data = {
        "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":text,
                "buttons":[
                    {
                        "type":"postback",
                        "title": options[0][0],
                        "payload": options[0][1]
                    },
                    {
                        "type":"postback",
                        "title": options[1][0],
                        "payload": options[1][1]
                    }
                ]
            }
        }
    }

    sendRequest(sender_id, message_data)

def sendImageMessage(sender_id, imageURL):

    message_data = {
        "attachment":{
            "type":"image",
            "payload":{
                "url":imageURL
            }
        }
    }

    sendRequest(sender_id, message_data)

def sendText(sender_id, text):
    #log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    
    message_data = {"text":text}

    sendRequest(sender_id, message_data)

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
    print(str(message))
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)

