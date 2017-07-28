import config
import requests
import json

"""
Support function for call opendata api
"""
def call_opendata(path, params=None):
    return requests.get(config.OPENDOTA_ENDPOINT + path, params=params).json()

"""
Send the message text to recipient with id recipient.
"""
def send_message(sender_id, text, options=None):
    message = {
        "recipient": {"id": sender_id},
        "message": {"text": text},
    }
    if options is not None:
        message["message"]["quick_replies"] = options

    r = requests.post(config.FB_ENDPOINT,
        params={"access_token": config.PAT},
        data=json.dumps(message),
        headers={'Content-type': 'application/json'}
    )
    if r.status_code != requests.codes.ok:
        print(r.text)

"""
Send image to receipient
The picture will be uploaded to messenger
"""
def send_image(sender_id, image_url):
    message = {
        'recipient': {
            'id': sender_id,
        },
        'message': {
            'attachment': {
                'type': "image",
                'payload': {
                    'url': image_url,
                },
            },
        },
    }
    r = requests.post(config.FB_ENDPOINT,
        params={"access_token": config.PAT},
        data=json.dumps(message),
        headers={'Content-type': 'application/json'}
    )
    if r.status_code != requests.codes.ok:
        print(r.image_url)

def send_indicator(sender_id, action):
    message = {
        'recipient': {
            'id': sender_id,
        },
        'sender_action': action,
    }
    requests.post(config.FB_ENDPOINT,
        params={"access_token": config.PAT},
        data=json.dumps(message),
        headers={'Content-type': 'application/json'}
    )
