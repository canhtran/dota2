from flask import Flask, request
import json
import config
import re
import common
import PlayerProfile

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.

@app.route('/', methods=['GET'])
def handle_verification():
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge', '')

    if verify_token == config.MESSENGER_TOKEN:
        print "Verification successful! GL-HF"
        return challenge
    else:
        print "Verification failed! GGWP !"
        return 'Error, GGWP!'

@app.route('/', methods=['POST'])
def handle_messages():
    body = json.loads(request.get_data())
    print body

    if body.get("object") != "page":
        return 'Noobs, GGWP !'

    for sender_id, message in messaging_events(body):
        print "Incoming from %s: %s" % (sender_id, message)
        receive_message(sender_id, message)
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

if __name__ == '__main__':
    app.run(debug=True)
