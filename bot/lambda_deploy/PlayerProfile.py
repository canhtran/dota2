import common

"""
Generate player profile based on Account ID
"""
def profile_generator(account_id, sender_id):
    player = get_player(account_id)

    if player.get("profile"):
        common.send_message(sender_id, "Hey, Let me see what I have about this player... ")
        common.send_message(sender_id, "Steam Account ID: %s" % account_id)
        name = player["profile"]["personaname"]
        common.send_message(sender_id, "Ah ha! I know this person, this is: %s 💎" % name)
        common.send_image(
            sender_id,
            player.get("profile").get("avatarfull"),
        )

        common.send_message(sender_id, "I love the avatar 💓. Let me find some insights about this player")

        """Win Rate
        """
        wl = get_wl(account_id)
        total_matches = wl["lose"] + wl["win"]
        winrate = round((wl["win"] / float(total_matches)) * 100,2)
        common.send_message(
            sender_id,
            "Hmm... your winrate is %s" % winrate + "%. That's not too bad."
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
        common.send_message(sender_id, stat_mess)
        common.send_message(sender_id, "That's the average number you got per match. Keep it up!")
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
