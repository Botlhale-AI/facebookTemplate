from flask import Flask, request, json
import requests
from datetime import datetime
from threading import Timer
import urllib.request

def send_message(recipient_id, text, buttons=False):
    """Send a response to Facebook"""
    if buttons:
        buttons_json = []
        for button in buttons:
            buttons_json.append({
                            "type":"postback",
                            "payload": button['payload'],
                            "title":button['title'],
                        })
        print(buttons_json)
        payload = {
                "recipient":{
                    "id":recipient_id,
                },
                "message":{
                    "attachment":{
                    "type":"template",
                    "payload":{
                        "template_type":"button",
                        "text":text,
                        "buttons": buttons_json
                        
                    }
                    }
                }
                }
    else:
        payload = {
            'message': {
                'text': text
            },
            'recipient': {
                'id': recipient_id
            },
            'notification_type': 'regular'
        }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()

def get_bot_response(message):
    """This is just a dummy function, returning a variation of what
    the user said. Replace this function with one connected to chatbot."""
    print(message)
    return "{}".format(message)

def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

def respond(sender, message, buttons=False):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    
    response = get_bot_response(message)
    print(response)
    send_message(sender, response, buttons)

def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))

def is_postback(message):
    """Check if the message is a message from the user with a payload"""
    return (message.get('postback') and
            message['postback'].get('payload') and
            not message['postback'].get("is_echo"))

def is_speech(message):
    """Check if the message is speech"""
    try:
        return (message.get('message') and
                message['message'].get('attachments')[0]['type']=='audio')
    except:
        return False

def generateAuthToken():
    # Generate Auth Token
    payload={
        'REFRESH_TOKEN': refreshToken,
        }
    IdToken = json.loads(requests.request("POST", generateAuthTokenUrl, data=payload).content)['AuthenticationResult']['IdToken']
    print(IdToken)
    # Store IdToken in config.json
    with open('config.json') as json_file:
        parameters = json.load(json_file) 
    parameters['IdToken'] = IdToken
    open('config.json', 'w').write(json.dumps(parameters))
    return IdToken

app = Flask(__name__)
app.secret_key = 'any random string'

with open('config.json') as json_file:
    parameters = json.load(json_file) 
    print("Type:", type(parameters))
    print(parameters)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = parameters['VERIFY_TOKEN'] # <paste your verify token here>
PAGE_ACCESS_TOKEN = parameters['PAGE_ACCESS_TOKEN']# paste your page access token here>"

# API Endpoints
generateAuthTokenUrl = "https://dev-botlhale.io/generateAuthToken"
connectUrl = "https://dev-botlhale.io/connect"
sendMessageUrl = "https://dev-botlhale.io/message"

# Chatbot Constants
BotID = parameters['BotID']
refreshToken = parameters['refreshToken']
LanguageCode = parameters['LanguageCode']
parameters['MessageType'] = 'text'
MessageType = parameters['MessageType']
ResponseType = parameters['ResponseType']
open('config.json', 'w').write(json.dumps(parameters))

@app.before_first_request
def before_first_request():
    generateAuthToken()
    x=datetime.today()
    y = x.replace(day=x.day, hour=0, minute=5, second=0, microsecond=0)
    delta_t=y-x
    secs=delta_t.total_seconds()
    print('secs', secs)
    t = Timer(secs, generateAuthToken)
    t.start()

@app.route("/webhook",methods=['GET','POST'])
def listen():
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        SpeechFile = None
        text = None
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x) or is_postback(x) or is_speech(x):
                with open('config.json') as json_file:
                    parameters = json.load(json_file) 

                # Configure response
                if is_user_message(x):
                    text = x['message']['text']
                    sender_id = x['sender']['id']
                elif is_postback(x):
                    text = x['postback']['payload']
                    sender_id = x['sender']['id']
                elif is_speech(x):
                    sender_id = x['sender']['id']
                    SpeechUrl = x['message']['attachments'][0]['payload']['url']
                    urllib.request.urlretrieve(SpeechUrl, '{}.wav'.format(sender_id))
                    SpeechFile = '{}.wav'.format(sender_id)
                    parameters['MessageType'] = 'speech'
                    open('config.json', 'w').write(json.dumps(parameters))

                # Chatbot Constants
                with open('config.json') as json_file:
                    parameters = json.load(json_file) 

                BotID = parameters['BotID']
                LanguageCode = parameters['LanguageCode']
                MessageType = parameters['MessageType']
                ResponseType = parameters['ResponseType']
                IdToken = parameters['IdToken']
                payload={
                    'BotID': BotID,
                    'LanguageCode': LanguageCode,
                    'FBsenderID': sender_id,
                    'MessageType': MessageType,
                    'ResponseType': ResponseType,
                    'TextMsg': text
                }

                try:
                    files=[
                    ('SpeechFile',(SpeechFile,open(SpeechFile,'rb'),'audio/wav'))
                    ]
                except:
                    files=[
                
                    ]

                print('payload', payload)
                headers = {"Authorization": "Bearer {}".format(IdToken)}
                response = json.loads(requests.request("POST", sendMessageUrl, headers=headers, data=payload, files=files).content)
                print('response',response)
                for text in response['TextResponse']:
                    if response['TextResponse'].index(text) == len(response['TextResponse'])-1:
                        respond(sender_id, text, response['Buttons'])
                    else:
                        respond(sender_id, text, False)

        return "ok"


if __name__ == "__main__":
    app.debug = True
    app.run(port='5000')