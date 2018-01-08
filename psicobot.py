import os, sys
from flask import Flask, request
import json
import requests
#from utils import wit_response
from pymessenger import Bot
from os import environ
import re

app = Flask(__name__)

#v_token = environ.get('FB_VERIFY_TOKEN')
#a_token = environ.get('FB_ACCESS_TOKEN')

v_token = "blondiebytes"
a_token = "EAADZBqZBZC8rAIBAPDztnVHeGZB7slQzZBZBiZBsZBl5XrCrlpJa6Oo5mQr0kfUBdci5LvVuOg9U1RhaHDLX9nkbQSigIDqcgnmGiY6KU2zeMZCZBPZBekdzgyaeUupy1fiUmTjwfHw0FFrzWADZBPYWmO3b3BZABmJ5J2BsJO7GQiDg23hvKfvOFdpjm"

bot = Bot(a_token)

respuestas = []
consentimiento_accepted = False

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
                            decideMessage(sender_id, message_text)
                        else:
                            message_text = "no text"
                        

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
                        "type":"web_url",
                        "url": "https://github.com/IsaacRodgz/ChatbotDepression/blob/master/README.md",
                        "title":"Ir a consentimiento"
                    }
        ]

        bot.send_button_message(sender_id, "Hola *user_name*, me llamo pumita :D. Me da mucho gusto que te intereses en tu bienestar. Para empezar, me gustaría que leas este consentimiento informado que habla acerca de lo que hacemos en pumabot por la salud ;)", buttons)

        buttons = [
                    {
                        "type":"postback",
                        "title": "Si",
                        "payload": "si_acepta_consentimiento"
                    },
                    {
                        "type":"postback",
                        "title": "No",
                        "payload": "no_acepta_consentimiento"
                    }
        ]

        bot.send_button_message(sender_id, "He leido y estoy de acuerdo con el consentimiento informado.", buttons)

    elif "no_acepta_consentimiento" in text:
        bot.send_text_message(sender_id, "Si cambias de opinión háblame de nuevo :)")

    elif "si_acepta_consentimiento" in text:

        bot.send_text_message(sender_id, "Muy bien *user_name* vamos a comenzar ;). ¿Qué frase describe mejor como te has sentido durante las últimas dos semanas, incluido el dia de hoy?. Empecemos con la tristeza.\n\n*Frase_a.* No me siento triste.\n*Frase_b.* Me siento triste la mayor parte del tiempo.\n*Frase_c.* Estoy triste todo el tiempo.\n*Frase_d.* Me siento tan triste y desgraciado que no puedo soportarlo.")

    elif re.search(r' [abcd]|^[abcd]', text) and "muy bien *user_name* vamos a comenzar ;)" not in text:
        print("*****")        
        print(text)
        print("*****")
        respuestas.append(text[text.index(re.search(r' [abcd]|^[abcd]', text).group(0))+1])

    else:
        bot.send_text_message(sender_id, "No entiendo lo que dices.")

    print(respuestas)

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

