from flask import Flask, request
import json
import requests
import config

app = Flask(__name__)

# General backup for testing with Lambda AWS Services

"""
Lambda handler
"""
def handler(event, context):
    if event.get("context").get("http-method") == "GET":
        return handle_verification(event, context)
    else:
        return handle_messages(event, context)

"""
Catch the POST request from Facebook to verify the api.
Check with token and return the challenge
"""
def handle_verification(event, context):
    querystring = event.get("params").get("querystring")
    verify_token = querystring.get("hub.verify_token")
    challenge = querystring.get("hub.challenge")

    if verify_token == config.MESSENGER_TOKEN:
        print "Verification successful! GL-HF"
        return int(challenge)
    else:
        print "Verification failed! GGWP !"
        return 'Error, GGWP!'

"""
Catch the message which key in from messenger
"""
def handle_messages(event, context):
    body = event.get("body-json")

    if body.get("object") != "page":
        return 'Noobs, GGWP !'

    for sender, message in messaging_events(body):
        print "Incoming from %s: %s" % (sender, message)
        receive_message(sender, message)
        return "ok"

@app.route('/', methods=['GET'])
def handle_verification():
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge', '')

    if challenge == config.MESSENGER_TOKEN:
        print "Verification successful! GL-HF"
        return int(challenge)
    else:
        print "Verification failed! GGWP !"
        return 'Error, GGWP!'

@app.route('/', methods=['POST'])
def handle_messages():
    body = json.loads(request.get_data())
    print body

    if body.get("object") != "page":
        return 'Noobs, GGWP !'

    for sender, message in messaging_events(body):
        print "Incoming from %s: %s" % (sender, message)
        receive_message(sender, message)
        return "ok"

"""
Generate tuples of (sender_id, message_text) from the
provided payload.
"""
def messaging_events(data):
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
        else:
            yield event["sender"]["id"], "I can't echo this"

def receive_message(sender, message):
    send_message(config.PAT, sender, message)

"""
Send the message text to recipient with id recipient.
"""
def send_message(token, recipient, text):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
        "recipient": {"id": recipient},
        "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print r.text

if __name__ == '__main__':
  app.run(debug=True)
