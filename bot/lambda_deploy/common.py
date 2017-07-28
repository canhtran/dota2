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
    payload = {
        'recipient': {
            'id': sender_id,
        },
        'message': {
            'text': text[:640],
        },
    }
    if options is not None:
        payload["message"]["quick_replies"] = options
    return send_api(payload)

"""
Send image to receipient
The picture will be uploaded to messenger
"""
def send_image(sender_id, image_url):
    return send_api({
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
    })

"""
send_indicator will execute the action on the messenger
https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions
"""
def send_indicator(sender_id, action):
    send_api({
        'recipient': {
            'id': sender_id,
        },
        'sender_action': action,
    })
"""
send_api sends the payload to FB Messenger API
"""
def send_api(payload):
    url = "%s?access_token=%s" % (
        config.FB_ENDPOINT,
        config.PAT,
    )
    return requests.post(
        url,
        json=payload
    )
