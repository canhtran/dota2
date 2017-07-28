# -*- coding: utf-8 -*-
import json
import requests
import re
import logging

PAT = 'EAAKYTN5BHzUBAJSCZAxifrX2jNN3fQ8agaZCq3kup1ZCG1KXBnFux84J46ndvaBgJYZAkZBrI6QkaxRkMfTuaiZCj4u2le8ivvsIWrSRYvwYu41Cyk0o8gJcaok3L4i2VqOLuoqL4ZAfNdFizjV1SoioY2KNENkxqVhqwrZC9GNGTAZDZD'
MESSENGER_TOKEN = 'dota_my_password_verify_me'
FB_ENDPOINT = 'https://graph.facebook.com/v2.6/me/messages'
OPENDOTA_ENDPOINT = 'https://api.opendota.com/api/'

"""
Setup the logger
"""
logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""
Lambda handler
"""
def handler(event, context):
    if keys_exist(event, ["params","querystring","hub.verify_token","hub.challenge"]):
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

    if verify_token == MESSENGER_TOKEN:
        print("Verification successful! GL-HF")
        return int(challenge)
    else:
        print("Verification failed! GGWP !")
        return 'Error, GGWP!'

"""
Catch the message which key in from messenger
"""
def handle_messages(event, context):
    body = event.get("body-json")

    if body.get("object") != "page":
        return 'Noobs, GGWP !'

    for sender, message in messaging_events(body):
        print("Incoming from %s: %s" % (sender, message))
        receive_message(sender, message)
        return "ok"


"""
Generate tuples of (sender_id, message_text) from the
provided payload.
"""
def messaging_events(data):
    messaging_events = data["entry"][0]["messaging"]
    print("Message Event")
    print(messaging_events)
    for event in messaging_events:
        if event.get("message"):
            message = event.get("message")
            if message.get("quick_reply"):
                yield event.get("sender").get("id"), message.get("quick_reply").get("payload").encode('unicode_escape')
            else:
                yield event.get("sender").get("id"), message.get("text").encode('unicode_escape')
        else:
            yield event.get("sender").get("id"), "Dota 2 Coordinator is not connected, Mid Fail, GGWP."

"""
Process message from event (sender_id, message)
"""
def receive_message(sender_id, message):
    if not re.match('\d{5}', message.decode('utf-8')):
        dota2bot_username(message, sender_id)
    else:
        account_ids = re.findall('\d+', message.decode('utf-8'))
        if len(account_ids) > 1:
            dota2bot_multiple_ids(account_ids, sender_id)
        else:
            account_id = account_ids[0]
            dota2bot_single_id(account_id, sender_id)

"""
User key in Username
"""
def dota2bot_username(text, sender_id):
    accounts = call_opendata("/search", params={'q':text})
    if len(accounts) > 1:
        options = []
        for account in accounts[:10]:
            options.append({
                'content_type': "text",
                'title': account.get("personaname"),
                'payload': account.get("account_id"),
                'image_url': account.get("avatarfull"),
            })
        send_message(sender_id, "All Pick, Please choose your account", options=options)
    elif len(accounts) == 1:
        dota2bot_single_id(account.get("account_id"), sender_id)
    else:
        send_message(sender_id, "Sorry Noob, I cannot find your username, choose another one ?")

"""
User key in multiple account ids
"""
def dota2bot_multiple_ids(account_ids, sender_id):
    options = []
    i = 0
    for account_id in account_ids[:10]:
        player = get_player(account_id)
        if player.get("profile"):
            i += 1
            options.append({
                'content_type': "text",
                'title': player.get("profile").get("personaname"),
                'payload': player.get("profile").get("account_id"),
                'image_url': player.get("profile").get("avatarfull"),
            })
    if i > 0:
        send_message(sender_id, "Single Draft, please pick one account only", options=options)
    else:
        send_message(sender_id, "Don't bluff me, Are you sure this is Dota profile ?")

"""
User key in only one account_id
"""
def dota2bot_single_id(account_id, sender_id):
    profile_generator(account_id, sender_id)

def keys_exist(obj, keys):
    for key in keys:
        if find_item(obj, key) is None:
            return False
    return True

def find_item(obj, key):
    item = None
    if key in obj: return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            item = find_item(v, key)
            if item is not None:
                return item

"""
Generate player profile based on Account ID
"""
def profile_generator(account_id, sender_id):
    player = get_player(account_id)

    if player.get("profile"):
        send_message(sender_id, "Hey, I know you ! ")
        send_message(sender_id, "Your Steam Account ID: %s" % account_id)
        name = player["profile"]["personaname"]
        send_message(sender_id, "Name: %s" % name)
        send_image(
            sender_id,
            player["profile"]["personaname"],
        )

        send_message(sender_id, "Let me find some insights about you")

        """Win Rate
        """
        wl = get_wl(account_id)
        total_matches = wl["lose"] + wl["win"]
        winrate = (wl["win"] / float(total_matches)) * 100
        send_message(
            sender_id,
            "Winrate: %s" % winrate + "%"
        )
        send_message(sender_id, "That's great!!!")

        """Player statistics
        """
        send_message(
            sender_id,
            "I can help you calculate some statistics based on your %s matches:" % total_matches
        )
        player_stats = get_player_statistics(account_id)
        test_mess = "Message \n with a line break"
        stat_mess = ''
        for index, value in player_stats.items():
            stat_mess += " -- %s: %s \n" % (index, value)
        send_message(sender_id, stat_mess)
        send_message(sender_id, "Hmm.. That's the average number you got per match. Keep it up!")
    else:
        send_message(sender_id, "Are you kidding me? This account is invalid or private.")

"""
Get player details from opendota api
"""
def get_player(account_id):
    return call_opendata("/players/" + account_id)

"""
Get Win-Lose from opendota api
"""
def get_wl(account_id):
    return call_opendata("/players/" + account_id + "/wl")

"""
Get totals statistics and do calculation
"""
def get_player_statistics(account_id):
    totals = call_opendata("/players/" + account_id + "/totals")
    statistics = {}
    for item in totals[:8]:
        statistics[item['field']] = item['sum'] / item['n']

    return statistics


"""
Support function for call opendata api
"""
def call_opendata(path, params=None):
    return requests.get(OPENDOTA_ENDPOINT + path, params=params).json()

"""
Send the message text to recipient with id recipient.
"""
"""
send_text_message will send a simple text message
if options are specified, the messewnger will display those options
"""
def send_message(sender_id, message_text, options=None):
    payload = {
        'recipient': {
            'id': sender_id,
        },
        'message': {
            'text': message_text[:640],
        },
    }
    if options is not None:
        payload["message"]["quick_replies"] = options
    return call_send_api(payload)

"""
send_image will upload an image to the messenger
"""
def send_image(sender_id, image_url):
    return call_send_api({
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
    call_send_api({
        'recipient': {
            'id': sender_id,
        },
        'sender_action': action,
    })

"""
call_send_api sends the payload to FB Messenger API
"""
def call_send_api(payload):
    url = "%s?access_token=%s" % (
        FB_ENDPOINT,
        PAT,
    )
    print(url)
    print(payload)
    return requests.post(
        url,
        json=payload
    )
