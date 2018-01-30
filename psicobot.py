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
names = {}
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
                    # TODO: Chatbot must return a message with NLP
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

    if sender_id not in names:

        print("Adding new name....")

        # Get user info. requests.get returns string with the info
        r = requests.get("https://graph.facebook.com/v2.6/1492366360818359?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token="+a_token).text
        
        # Convert string to dict
        r = json.loads(r)

        # Get user first_name and last_name
        names[sender_id] = (r["first_name"], r["last_name"])

    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(names[sender_id][0])
    print(text)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    if "get_started_payload" == text:

        welcome_text = "Hola "+names[sender_id][0]+", me llamo pumita :D. Me da mucho gusto que te intereses en tu bienestar. Dado que soy un robot, la manera en que nos podremos comunicar es por medio de botones, ¿Los puedes ver?"

        buttons = [
                    {
                        "content_type":"text",
                        "title": "Si",
                        "payload": "si_ve_botones"
                    },
                    {
                        "content_type":"text",
                        "title": "No",
                        "payload": "no_ve_botones"
                    }
        ]

        sendTyping(sender_id)
        send_quick_reply(sender_id, welcome_text, buttons)

    elif "si_ve_botones" in text:
        sendTyping(sender_id)
        bot.send_text_message(sender_id, "Perfecto "+names[sender_id][0]+" vamos a comenzar")
        sendImageMessage(sender_id, "https://i.imgur.com/P785top.jpg")

        buttons = [
            {
                "content_type":"text",
                "title":"¡Listo!",
                "payload":"go_adelante"
            }
        ]

        sendTyping(sender_id)
        send_quick_reply(sender_id, "¿Estás listo? Te aplicaré un test, esto será muy breve.", buttons)

    elif "no_ve_botones" in text:
        sendTyping(sender_id)
        bot.send_text_message("Por favor comunícale la situación al instructor")

    elif "go_adelante" in text:

        sendTyping(sender_id)
        bot.send_text_message(sender_id, "Por favor selecciona el botón que contenga la letra que represente su estado actual o el estado con el que mejor se identifique")

        sendTyping(sender_id)
        pregunta1 = "\n1. Me he divertido mucho durante las últimas dos semanas.\n\n"

        buttons = [
            {
                "content_type":"text",
                "title":"Nunca",
                "payload":"1_a"
            },
            {
                "content_type":"text",
                "title":"De vez en cuando",
                "payload":"1_b"
            },
            {
                "content_type":"text",
                "title":"Usualmente",
                "payload":"1_c"
            },
            {
                "content_type":"text",
                "title":"Muy a menudo",
                "payload":"1_d"
            },
            {
                "content_type":"text",
                "title":"Siempre",
                "payload":"1_e"
            }
        ]

        sendTyping(sender_id)
        send_quick_reply(sender_id, pregunta1, buttons)

    elif "no_acepta_consentimiento" in text:
        sendTyping(sender_id)
        bot.send_text_message(sender_id, "Si cambias de opinión háblame de nuevo :)")

    elif "si_acepta_consentimiento" in text:
        sendTyping(sender_id)
        bot.send_text_message(sender_id, "Si cambias de opinión háblame de nuevo :)")

    elif re.search(r'^[0-9]+\_[abcdefghij]$', text):
        respuestas.append(text)
        if len(respuestas) == 1:
            sendTyping(sender_id)
            bot.send_text_message(sender_id, "Muy bien, he guardado tu respuesta, continuemos.")
            sendImageMessage(sender_id, "https://i.imgur.com/Cn57NXT.jpg")

            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 1.")

            pregunta2 = "2. Disfruto del sexo.\n\n"

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"2_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"2_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"2_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"2_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"2_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta2, buttons)

        elif len(respuestas) == 2:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 2.")

            pregunta3 = "3. Estoy satisfecho con mi vida\n\n"

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"3_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"3_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"3_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"3_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"3_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta3, buttons)

        elif len(respuestas) == 3:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 3. Tu respuesta fue: "+text)

            pregunta4 = "4. Disfruto de la vida."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"4_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"4_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"4_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"4_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"4_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta4, buttons)

        elif len(respuestas) == 4:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 4. Tu respuesta fue: "+text)

            pregunta5 = "5. Pienso que mi vida ha sido un fracaso."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"5_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"5_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"5_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"5_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"5_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta5, buttons)

        elif len(respuestas) == 5:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 5. Tu respuesta fue: "+text)

            pregunta6 = "6. Siento que he sido mala persona."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"6_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"6_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"6_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"6_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"6_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta6, buttons)

        elif len(respuestas) == 6:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 6. Tu respuesta fue: "+text)

            pregunta7 = "7. Duermo sin descansar."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"7_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"7_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"7_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"7_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"7_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta7, buttons)

        elif len(respuestas) == 7:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 7. Tu respuesta fue: "+text)

            pregunta8 = "8. Me siento cansado todo el tiempo."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"8_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"8_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"8_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"8_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"8_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta8, buttons)

        elif len(respuestas) == 8:
            sendTyping(sender_id)
            bot.send_text_message(sender_id, "Ok ya falta menos para terminar "+names[sender_id][0]+" y podrás ver memes sobre el semestre ;)")
            #sendImageMessage(sender_id, "")
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 8. Tu respuesta fue: "+text)

            pregunta9 = "9. Necesito hacer un esfuerzo extra para comenzar a hacer algo."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"9_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"9_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"9_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"9_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"9_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta9, buttons)

        elif len(respuestas) == 9:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 9. Tu respuesta fue: "+text)

            pregunta10 = "10. Me siento con falta de energía y fuerza."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"10_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"10_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"10_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"10_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"10_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta10, buttons)

        elif len(respuestas) == 10:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 9. Tu respuesta fue: "+text)

            pregunta11 = "11. Creo que tengo un aspecto horrible."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"11_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"11_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"11_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"11_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"11_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta11, buttons)

        elif len(respuestas) == 11:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 9. Tu respuesta fue: "+text)

            pregunta12 = "12. Me siento deprimido."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"12_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"12_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"12_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"12_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"12_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta12, buttons)

        elif len(respuestas) == 12:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 9. Tu respuesta fue: "+text)

            pregunta13 = "13. Nada me hace feliz."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"13_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"13_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"13_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"13_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"13_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta13, buttons)

        elif len(respuestas) == 13:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 9. Tu respuesta fue: "+text)

            pregunta14 = "14. Me siento sin esperanza."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"14_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"14_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"14_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"14_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"14_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta14, buttons)

        elif len(respuestas) == 14:
            sendTyping(sender_id)
            #bot.send_text_message(sender_id, "Gracias por responder la pregunta 9. Tu respuesta fue: "+text)

            pregunta15 = "15. Me siento como si fuese a ser castigado."

            buttons = [
                {
                    "content_type":"text",
                    "title":"Nunca",
                    "payload":"15_a"
                },
                {
                    "content_type":"text",
                    "title":"De vez en cuando",
                    "payload":"15_b"
                },
                {
                    "content_type":"text",
                    "title":"Usualmente",
                    "payload":"15_c"
                },
                {
                    "content_type":"text",
                    "title":"Muy a menudo",
                    "payload":"15_d"
                },
                {
                    "content_type":"text",
                    "title":"Siempre",
                    "payload":"15_e"
                }
            ]

            sendTyping(sender_id)
            send_quick_reply(sender_id, pregunta15, buttons)

        elif len(respuestas) == 15:
            sendTyping(sender_id)
            bot.send_text_message(sender_id, "Gracias "+names[sender_id][0]+" , he guardado tus respuestas, estoy procesando los resultados. No desesperes como goku.")
            sendImageMessage(sender_id, "https://i.imgur.com/L8AWFBf.jpg")

    else:
        sendTyping(sender_id)
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
                "buttons":options
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

def sendTyping(recipient_id):
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
        "sender_action":"typing_on"
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

