# encoding: utf-8

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
    print("$$$$$$$$$$$$$$$$$inside webhook$$$$$$$$$$$$$$$$$$$$$$")
    log(data)
    print("$$$$$$$$$$$$$$$$$inside webhook$$$$$$$$$$$$$$$$$$$$$$")
    log("\n")

    if data['object'] == 'page':
        for entry in data['entry']:
            if entry.get("messaging"):
                for messaging_event in entry['messaging']:

                    sender_id = messaging_event["sender"]["id"] # FB ID of the person sending you the message
                    recipient_id = messaging_event['recipient']['id'] # Chatbot ID

                    # Text Message
                    # TODO: Chatbot must return a message
                    if messaging_event.get("message"):  # someone sent us a message
                        if messaging_event['message'].get('is_echo'):  # Discard text, it's just echoing sent messages to user
                            pass
                        elif messaging_event['message'].get('quick_reply'):
                            message_text = messaging_event['message']['quick_reply']['payload']  # the message's text
                            decideMessage(sender_id, message_text)
                        elif 'text' in messaging_event['message']:
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

    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(text)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    if "get_started_payload" == text:
        
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

        pregunta1 = "Muy bien *user_name* vamos a comenzar ;). ¿Qué frase describe mejor como te has sentido durante las últimas dos semanas, incluido el dia de hoy?. Te molestaron cosas que usualmente no te molestan.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

        buttons = [
            {
                "content_type":"text",
                "title":"A",
                "payload":"1_a"
            },
            {
                "content_type":"text",
                "title":"B",
                "payload":"1_b"
            },
            {
                "content_type":"text",
                "title":"C",
                "payload":"1_c"
            },
            {
                "content_type":"text",
                "title":"D",
                "payload":"1_d"
            }
        ]

        send_quick_reply(sender_id, pregunta1, buttons)

    elif re.search(r'^[0-9]+\_[abcdefghij]$', text):
        respuestas.append(text)
        if len(respuestas) == 1:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 1. Tu respuesta fue: "+text)

            pregunta2 = "No te sentiste con ganas de comer.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"2_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"2_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"2_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"2_d"
                }
            ]
            
            send_quick_reply(sender_id, pregunta2, buttons)


        elif len(respuestas) == 2:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 2. Tu respuesta fue: "+text)

            pregunta3 = "Sentías que no podías quitarte de encima la tristeza aún con la ayuda de tu familia o amigos.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"3_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"3_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"3_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"3_d"
                }
            ]

            send_quick_reply(sender_id, pregunta3, buttons)

        elif len(respuestas) == 3:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 3. Tu respuesta fue: "+text)

            pregunta4 = "Sentías que eras tan buena/bueno como cualquier otra persona.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"4_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"4_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"4_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"4_d"
                }
            ]

            send_quick_reply(sender_id, pregunta4, buttons)

        elif len(respuestas) == 4:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 4. Tu respuesta fue: "+text)

            pregunta5 = "Tenías dificultad en mantener tu mente en lo que estabas haciendo.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"5_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"5_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"5_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"5_d"
                }
            ]

            send_quick_reply(sender_id, pregunta5, buttons)

        elif len(respuestas) == 5:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 5. Tu respuesta fue: "+text)

            pregunta6 = "Te sentías deprimida/deprimido.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"6_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"6_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"6_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"6_d"
                }
            ]

            send_quick_reply(sender_id, pregunta6, buttons)

        elif len(respuestas) == 6:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 6. Tu respuesta fue: "+text)

            pregunta7 = "Sentías que todo lo que hacías era un esfuerzo.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"7_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"7_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"7_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"7_d"
                }
            ]

            send_quick_reply(sender_id, pregunta7, buttons)

        elif len(respuestas) == 7:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 7. Tu respuesta fue: "+text)

            pregunta8 = "Te sentías optimista sobre el futuro.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"8_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"8_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"8_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"8_d"
                }
            ]

            send_quick_reply(sender_id, pregunta8, buttons)

        elif len(respuestas) == 8:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 8. Tu respuesta fue: "+text)

            pregunta9 = "Pensaste que tu vida había sido un fracaso.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"9_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"9_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"9_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"9_d"
                }
            ]

            send_quick_reply(sender_id, pregunta9, buttons)

        elif len(respuestas) == 9:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 9. Tu respuesta fue: "+text)

            pregunta10 = "Te sentías con miedo.\n\n*A.* Raramente o ninguna vez (Menos de un día).\n*B.* Alguna o pocas veces (1-2 días).\n*C.* Ocasionalmente o una buena parte del tiempo (3-4 días).\n*D.* La mayor parte o todo el tiempo (5-7 días)."

            buttons = [
                {
                    "content_type":"text",
                    "title":"A",
                    "payload":"10_a"
                },
                {
                    "content_type":"text",
                    "title":"B",
                    "payload":"10_b"
                },
                {
                    "content_type":"text",
                    "title":"C",
                    "payload":"10_c"
                },
                {
                    "content_type":"text",
                    "title":"D",
                    "payload":"10_d"
                }
            ]

            send_quick_reply(sender_id, pregunta10, buttons)

        elif len(respuestas) == 10:
            bot.send_text_message(sender_id, "Gracias por responder la pregunta 10. Tu respuesta fue: "+text)

    else:
        bot.send_text_message(sender_id, "No entiendo lo que dices.")

    print("%%%%%%%%%%%%%%%%")
    print(respuestas)
    print("%%%%%%%%%%%%%%%%")

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

def send_quick_reply(sender_id, text, buttons):
    message_data = {
            "text": text,
            "quick_replies":
            [
                
            ]
    }

    for button in buttons:
        message_data['quick_replies'].append(button)

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

