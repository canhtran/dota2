import common
import pickle
import numpy as np
import pandas as pd

"""
Generate player profile based on Account ID
"""
def profile_generator(account_id, sender_id):
    player = get_player(account_id)

    if player.get("profile"):
        common.send_indicator(sender_id, "typing_on")
        common.send_message(sender_id, "Hey, Let me see what I have about this player... ")
        common.send_message(sender_id, "Steam Account ID: %s" % account_id)
        name = player["profile"]["personaname"]
        common.send_message(sender_id, "Ah ha! I know this person, this is: %s 💎" % name)
        common.send_indicator(sender_id, "typing_on")
        common.send_image(
            sender_id,
            player.get("profile").get("avatarfull"),
        )

        options = [
            {
                'content_type': "text",
                'title': "Yes. It corrects !",
                'payload': str(player.get("profile").get("account_id")) + "-details",
            },
            {
                'content_type': "text",
                'title': "I'm feeling good",
                'payload': "STOPP_FB_CODE_404"
            }
        ]
        common.send_message(sender_id, "Is this the player you wanna check ? Do you want me to find some insights ?", options=options)
    else:
        common.send_message(sender_id, "Are you kidding me? This account is invalid or private.")

    return "ok"

"""
Provide details of player with some simple statistics
Input: account_id, sender_id
"""
def profile_details(account_id, sender_id):
    common.send_message(sender_id, "Let me find some insights about this player. Btw, I love the avatar 💓. ")
    common.send_indicator(sender_id, "typing_on")
    """Win Rate
    """
    wl = get_wl(account_id)
    total_matches = wl["lose"] + wl["win"]
    winrate = round((wl["win"] / float(total_matches)) * 100,2)
    common.send_message(
        sender_id,
        "Hmm... the winrate is %s" % winrate + "%. That's not too bad."
    )

    """Player statistics
    """
    common.send_message(
        sender_id,
        "I can help you calculate some statistics based on %s matches:" % total_matches
    )
    player_stats = get_player_statistics(account_id)
    stat_mess = ''
    for index, value in player_stats.items():
        stat_mess += "👉 %s: %s\n" % (index, value)
    common.send_indicator(sender_id, "typing_on")
    common.send_message(sender_id, stat_mess)
    common.send_message(sender_id, "That's the average number per match. Keep it up!")

    options = [
        {
            'content_type': "text",
            'title': "Of course, for sure !",
            'payload': str(account_id) + "-recommendation",
        },
        {
            'content_type': "text",
            'title': "I'm feeling good",
            'payload': "STOPP_FB_CODE_404"
        }
    ]
    common.send_message(sender_id, "Do you want me to recommend some heroes for you ?", options=options)

"""
Collect heroes and call recommendation engine
"""
def players_recommendation(account_id, sender_id):
    common.send_message(sender_id, "Let me check about his/her heroes...")
    player_heroes = get_player_heroes(account_id)
    all_heroes = pd.read_csv("data/heroes.csv")
    heroes = []
    for idex, row in all_heroes.iterrows():
        hero = {}
        hero["id"] = row["id"]
        hero["localized_name"] = row["localized_name"]
        hero["main_role"] = row["main_role"]
        heroes.append(hero)

    heroes_hash = get_heroes_hash(heroes)

    for i, hero in enumerate(player_heroes[:5]):
        hero_ = heroes_hash[int(hero.get("hero_id"))]
        if i == 0:
            mess = "He/she played %d times with %s" % (
                hero.get("games"),
                hero_.get("localized_name"),
            )
        else:
            mess = "%d times with %s" % (
                hero.get("games"),
                hero_.get("localized_name"),
            )

        common.send_message(sender_id, mess)
        common.send_indicator(sender_id, "typing_on")

    player_stats = get_player_statistics(account_id)
    all_roles = {0: 'carry', 1: 'mid', 2: 'offlane', 3: 'support'}
    model_input = []
    for index, value in player_stats.items():
        model_input.append(value)

    clf = pickle.load(open("model/finalized_model.pkl", "rb" ))
    fv = np.array(model_input).reshape((1,-1))
    pred = clf.predict(fv)
    position = all_roles[pred[0]]
    common.send_message(
        sender_id,
        "Base on the profile, I think that he/she is suitable in %s position" % position
    )
    common.send_message(sender_id, "Some of heroes I think you may consider: ")
    df_rec = all_heroes[all_heroes['main_role'] == str(position)].sample(3)
    mess = ''
    dotafire = 'https://www.dotafire.com/dota-2/hero/'
    for idex, row in df_rec.iterrows():
        link = dotafire + str(row['localized_name']) + '-' + str(row['guide'])
        mess += "👉 %s: %s\n" % (row['localized_name'], link)

    common.send_message(sender_id, mess)

    common.send_message(sender_id, "I hope that was helpful 🙃")
    common.send_message(sender_id, "I'm happy to help again!")


"""
Get player details from opendota api
"""
def get_player(account_id):
    return common.call_opendata("/players/" + account_id)

"""
Get Win-Lose from opendota api
"""
def get_wl(account_id):
    return common.call_opendata("/players/" + account_id + "/wl")

"""
Get totals statistics and do calculation
"""
def get_player_statistics(account_id):
    totals = common.call_opendata("/players/" + account_id + "/totals")
    statistics = {}
    for item in totals[:8]:
        statistics[item['field']] = round(item['sum'] / item['n'])

    return statistics

"""
Get heroes of players, only count if number of games > 0
"""
def get_player_heroes(account_id):
    return [h for h in common.call_opendata("/players/%s/heroes" % account_id) if h.get("games") > 0]

"""
get totals heroes
"""
def get_heroes():
    return common.call_opendata("/heroes")

"""
Build a mapping <look up> table for heroes
"""
def get_heroes_hash(all_heroes):
    h = {}
    for hero in all_heroes:
        h[hero.get("id")] = hero
    return h
