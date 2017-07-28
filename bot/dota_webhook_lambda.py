# -*- coding: utf-8 -*-
import json
import config
import re
import common
import PlayerProfile
import logging

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
    print event
    body = json.loads(event.get("body"))
    print body

    if body.get("object") != "page":
        return 'Noobs, GGWP !'

    for sender, message in messaging_events(body):
        print "Incoming from %s: %s" % (sender, message)
        logger.info(json.dumps(message))
        receive_message(sender, message)
        return "ok"


"""
Generate tuples of (sender_id, message_text) from the
provided payload.
"""
def messaging_events(data):
    messaging_events = data["entry"][0]["messaging"]
    print "Message Event"
    print messaging_events
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
    if not re.match('\d{5}', message):
        dota2bot_username(message, sender_id)
    else:
        account_ids = re.findall('\d+', message)
        if len(account_ids) > 1:
            dota2bot_multiple_ids(account_ids, sender_id)
        else:
            account_id = account_ids[0]
            dota2bot_single_id(account_id, sender_id)

"""
User key in Username
"""
def dota2bot_username(text, sender_id):
    accounts = common.call_opendata("/search", params={'q':text})
    if len(accounts) > 1:
        options = []
        for account in accounts[:10]:
            options.append({
                'content_type': "text",
                'title': account.get("personaname"),
                'payload': account.get("account_id"),
                'image_url': account.get("avatarfull"),
            })
        common.send_message(sender_id, "All Pick, Please choose your account", options=options)
    elif len(accounts) == 1:
        dota2bot_single_id(account.get("account_id"), sender_id)
    else:
        common.send_message(sender_id, "Sorry Noob, I cannot find your username, choose another one ?")

"""
User key in multiple account ids
"""
def dota2bot_multiple_ids(account_ids, sender_id):
    options = []
    i = 0
    for account_id in account_ids[:10]:
        player = PlayerProfile.get_player(account_id)
        if player.get("profile"):
            i += 1
            options.append({
                'content_type': "text",
                'title': player.get("profile").get("personaname"),
                'payload': player.get("profile").get("account_id"),
                'image_url': player.get("profile").get("avatarfull"),
            })
    if i > 0:
        common.send_message(sender_id, "Single Draft, please pick one account only", options=options)
    else:
        common.send_message(sender_id, "Don't bluff me, Are you sure this is Dota profile ?")

"""
User key in only one account_id
"""
def dota2bot_single_id(account_id, sender_id):
    PlayerProfile.profile_generator(account_id, sender_id)

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
