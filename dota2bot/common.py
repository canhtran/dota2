import config
import requests
import json

"""
Support function for call opendata api
"""
def call_opendata(path, params):
    return requests.get(config.OPENDOTA_ENDPOINT + path, params=params).json()

"""
Send the message text to recipient with id recipient.
"""
def send_message(sender_id, text, options=None):
    message = {
        "recipient": {"id": sender_id},
        "message": {"text": text.decode('unicode_escape')},
    }
    if options is not None:
        message["message"]["quick_replies"] = options

    r = requests.post(config.FB_ENDPOINT,
        params={"access_token": config.PAT},
        data=json.dumps(message),
        headers={'Content-type': 'application/json'}
    )
    if r.status_code != requests.codes.ok:
        print r.text
