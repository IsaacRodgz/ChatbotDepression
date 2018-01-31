# encoding: utf-8

from random import shuffle
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

global respuestas, names, nivel, parafraseo_indices, parafraseo, puntajes, parafraseos

respuestas = {}
names = {}
nivel = {}
parafraseo_indices = {}
parafraseo = {}
consentimiento_accepted = False
puntajes = {'1_a':1,'1_b':2,'1_c':3,'1_d':4,'1_e':5,
            '2_a':5,'2_b':4,'2_c':3,'2_d':2,'2_e':1,
            '3_a':1,'3_b':2,'3_c':3,'3_d':4,'3_e':5,
            '4_a':5,'4_b':4,'4_c':3,'4_d':2,'4_e':1,
            '5_a':1,'5_b':2,'5_c':3,'5_d':4,'5_e':5,
            '6_a':1,'6_b':2,'6_c':3,'6_d':4,'6_e':5,
            '7_a':1,'7_b':2,'7_c':3,'7_d':4,'7_e':5,
            '8_a':1,'8_b':2,'8_c':3,'8_d':4,'8_e':5,
            '9_a':1,'9_b':2,'9_c':3,'9_d':4,'9_e':5,
            '10_a':1,'10_b':2,'10_c':3,'10_d':4,'10_e':5,
            '11_a':1,'11_b':2,'11_c':3,'11_d':4,'11_e':5,
            '12_a':1,'12_b':2,'12_c':3,'12_d':4,'12_e':5,
            '13_a':1,'13_b':2,'13_c':3,'13_d':4,'13_e':5,
            '14_a':1,'14_b':2,'14_c':3,'14_d':4,'14_e':5,
            '15_a':1,'15_b':2,'15_c':3,'15_d':4,'15_e':5}
parafraseos = [
    # 1
    [
        "Mencionas que estas dos semanas usualmente te haz divertido.",
        "Mencionas que estas dos semanas te has divertido de vez en cuando.",
        "Mencionas que estas dos semanas no te has divertido."
    ],
    # 2
    [
        "Refieres que usualmente disfrutas del sexo",
        "Refieres que de vez en cuando disfrutas del sexo",
        "Refieres que no disfrutas del sexo"
    ],
    # 3
    [
        "Consideras usualmente estar satisfecho con la vida",
        "Consideras estar de vez en cuando satisfecho con la vida",
        "Consideras no estar satisfecho con tu vida"
    ],
    # 4
    [
        "Manifiestas a veces disfrutar de la vida",
        "Manifiestas a veces disfrutar de la vida",
        "Manifiestas no disfrutar de la vida"
    ],
    # 5
    [
        "Que tu vida ha sido un fracaso (o al menos lo piensas la mayoría de las veces)",
        "Que tu vida ha sido un fracaso (o al menos lo piensas la mayoría de las veces)",
        "Que tu vida ha sido un fracaso (o al menos lo piensas la mayoría de las veces)"
    ],
    # 6
    [
        "Sientes que usualmente eres una mala persona",
        "Sientes que muy a menudo eres una mala persona",
        "Sientes que siempre haz sido una mala persona"
    ],
    # 7
    [
        "Te has dado cuenta que usualmente duermes sin descansar",
        "Te has dado cuenta que muy a menudo duermes sin descansar",
        "Te has dado cuenta que duermes sin descansar"
    ],
    # 8
    [
        "Usualmente estas cansado",
        "Estás cansado la mayor parte del tiempo",
        "Siempre estás cansado"
    ],
    # 9
    [
        "Haz observado que necesitas hacer un esfuerzo extra para comenzar a hacer algo",
        "Haz observado que necesitas hacer un esfuerzo extra para comenzar a hacer algo",
        "Haz observado que necesitas hacer un esfuerzo extra para comenzar a hacer algo"
    ],
    # 10
    [
        "También refieres tener usualmente una baja de energía y fuerza",
        "También refieres casi siempre tener una baja de energía o fuerza",
        "También refieres total baja de energía o fuerza"
    ],
    # 11
    [
        "A veces piensas que tienes un aspecto horrible",
        "A veces piensas que tienes un aspecto horrible",
        "Piensas que tienes un aspecto horrible"
    ],
    #12
    [
        "Te pasa que usualmente te sientes deprimido",
        "Sentirte deprimido es algo que muy a menudo te pasa",
        "Sentirte deprimido es algo que siempre refieres"
    ],
    #13
    [
        "En ocasiones piensas que nada te hace feliz",
        "Casi siempre piensas que nada te hace feliz",
        "Piensas que nada te hace feliz"
    ],
    #14
    [
        "Usualmente crees que no hay esperanza",
        "Consideras que a veces no hay esperanza",
        "Sientes que no tienes esperanzas"
    ],
    # 15
    [
        "A veces crees que vas a hacer castigado",
        "La mayoría del tiempo crees que vas a ser castigado",
        "Todo el tiempo crees que vas a ser castigado"
    ],
]


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

        # Initialize answers from user
        respuestas[sender_id] = []
    
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
        bot.send_text_message(sender_id, "Por favor selecciona el botón que represente su estado actual o el estado con el que mejor se identifique")

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

    elif "go_to_results" in text:
        sendTyping(sender_id)
        bot.send_text_message(sender_id, nivel[sender_id])

        print("°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°")
        print(parafraseo_indices[sender_id])

        parafraseo[sender_id] = ""
        text_concat_list = []

        for pi in parafraseo_indices[sender_id]:
            if parafraseo_indices[sender_id].index(pi) != 0:
                text_concat_list.append(parafraseos[pi[1]][pi[0]-3].lower())
            else:
                text_concat_list.append(parafraseos[pi[1]][pi[0]-3])

        text_concat = ', '.join(text_concat_list[:-1])
        text_concat += " y " + text_concat_list[-1]

        parafraseo[sender_id] = text_concat

        sendTyping(sender_id)
        bot.send_text_message(sender_id, "Esto significa que:")
        sendTyping(sender_id)
        bot.send_text_message(sender_id, parafraseo[sender_id])

        sendTyping(sender_id)
        text_send = "Tal vez te interese..."

        buttons = [
            {
                "content_type":"text",
                "title":"¿Qué hago?",
                "payload":"what_do"
            },
            {
                "content_type":"text",
                "title":"¿Qué es la depresión?",
                "payload":"what_is"
            }
        ]

        sendTyping(sender_id)
        send_quick_reply(sender_id, text_send, buttons)

    else:

        if re.search(r'^[0-9]+\_[abcdefghij]$', text):
            respuestas[sender_id].append(text)
            sendQuestion(sender_id, text)

        else:
            if(len(respuestas[sender_id]) < 15):
                sendTyping(sender_id)
                bot.send_text_message(sender_id, "Disculpa, por el momento no comprendo el lenguaje escrito. Volvamos a las preguntas.")
                sendQuestion(sender_id, text)
            else:
                sendTyping(sender_id)
                bot.send_text_message(sender_id, "Disculpa, por el momento no comprendo el lenguaje escrito. El  test ha terminado. Muchas gracias por participar :)")

    print("%%%%%%%%%%%%%%%%")
    print(respuestas)
    print("%%%%%%%%%%%%%%%%")

def sendQuestion(sender_id, text):

    if len(respuestas[sender_id]) == 1:
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

    elif len(respuestas[sender_id]) == 2:
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

    elif len(respuestas[sender_id]) == 3:
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

    elif len(respuestas[sender_id]) == 4:
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

    elif len(respuestas[sender_id]) == 5:
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

    elif len(respuestas[sender_id]) == 6:
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

    elif len(respuestas[sender_id]) == 7:
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

    elif len(respuestas[sender_id]) == 8:
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

    elif len(respuestas[sender_id]) == 9:
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

    elif len(respuestas[sender_id]) == 10:
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

    elif len(respuestas[sender_id]) == 11:
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

    elif len(respuestas[sender_id]) == 12:
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

    elif len(respuestas[sender_id]) == 13:
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

    elif len(respuestas[sender_id]) == 14:
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

    elif len(respuestas[sender_id]) == 15:
        sendTyping(sender_id)
        bot.send_text_message(sender_id, "Gracias "+names[sender_id][0]+" , he guardado tus respuestas, estoy procesando los resultados. No desesperes como goku.")
        sendImageMessage(sender_id, "https://i.imgur.com/L8AWFBf.jpg")


        # Calcula puntaje crudo

        puntaje_crudo = 0
        for resp in respuestas[sender_id]:
            puntaje_crudo += puntajes[resp]

        if puntaje_crudo >= 1 and puntaje_crudo <= 23:
            nivel[sender_id] = "Tuviste un puntaje de "+str(puntaje_crudo)+" y tu nivel corresponde a poca depresión"

        elif puntaje_crudo >= 24 and puntaje_crudo <= 29:
            nivel[sender_id] = "Tuviste un puntaje de "+str(puntaje_crudo)+" y tu nivel corresponde a algo de depresión"

        elif puntaje_crudo >= 30 and puntaje_crudo <= 35:
            nivel[sender_id] = "Tuviste un puntaje de "+str(puntaje_crudo)+" y tu nivel corresponde a bastante depresión"

        else:
            nivel[sender_id] = "Tuviste un puntaje de "+str(puntaje_crudo)+" y tu nivel corresponde a mucha depresión"


        # Sacar las 5 preguntas con puntaje más alto - parafraseo_indices
        
        parafraseo_indices[sender_id] = []
        puntaje_indice = []

        # Se construye lista de tuplas con la forma (puntaje, numero de pregunta)

        for i in range(len(respuestas[sender_id])):
            resp = respuestas[sender_id][i]
            puntaje_indice.append((puntajes[resp], i))
        
        shuffle(puntaje_indice)
        puntaje_indice.sort(key=lambda tup: tup[0], reverse=True)
        
        count = 0
        i = 0
    
        while count < 5 and i < len(puntaje_indice):
            if(puntaje_indice[i][0] > 2):
                count += 1
                parafraseo_indices[sender_id].append(puntaje_indice[i])
            i += 1
        
        parafraseo_indices[sender_id].sort(key=lambda tup: tup[1])
        
        # Enviar mensaje avisando que están listos los resultados

        sendTyping(sender_id)

        button = [
            {
                "content_type":"text",
                "title":"Ir a resultados",
                "payload":"go_to_results"
            }
        ]

        send_quick_reply(sender_id, "Gracias por esperar "+names[sender_id][0]+" , ya tengo tus resultados.", button)


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

