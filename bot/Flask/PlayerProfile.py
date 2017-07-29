import common

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

        common.send_message(sender_id, "I love the avatar 💓. Let me find some insights about this player")
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
            "I can help you calculate some statistics based on your %s matches:" % total_matches
        )
        player_stats = get_player_statistics(account_id)
        stat_mess = ''
        for index, value in player_stats.items():
            stat_mess += "👉 %s: %s\n" % (index, value)
        common.send_indicator(sender_id, "typing_on")
        common.send_message(sender_id, stat_mess)
        common.send_message(sender_id, "That's the average number per match. Keep it up!")

        player_heroes = get_player_heroes(account_id)
        all_heroes = get_heroes_hash()

        for i, hero in enumerate(player_heroes[:5]):
            hero_ = all_heroes[int(hero.get("hero_id"))]
            if i == 0:
                mess = "%s played %d times with %s" % (
                    name,
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

        common.send_message(sender_id, "I hope that was helpful 🙃")
        common.send_message(sender_id, "I'm happy to help again!")
    else:
        common.send_message(sender_id, "Are you kidding me? This account is invalid or private.")

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
def get_heroes_hash():
    h = {}
    heroes = get_heroes()
    for hero in heroes:
        h[hero.get("id")] = hero
    return h
