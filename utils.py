from wit import Wit

a_token = "GBHEFO5FOU4ASTGLBXPVC6IHK5Y2BDWV"

client = Wit(access_token = a_token)

def wit_response(message_text):
    resp = client.message(message_text)

    entity = None
    value = None

    try:
        entity = list(resp['entities'])[0]
        value = resp['entities'][entity][0]['value']
    except:
        pass                
        
    return (entity, value)

while True:
    message = str(input(">> "))
    print(">> {0}".format(wit_response(message)))
