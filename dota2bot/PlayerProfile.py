import common

"""
Generate player profile based on Account ID
"""
def profile_generator(account_id, sender_id):
    player = get_player(account_id)
    if player.get("profile"):
        common.send_message(sender_id, "Hey, I know you ! ")
        common.send_message(sender_id, "Your Steam Account ID: %s" % account_id)
        name = player.get("profile").get("personaname")
        common.send_message(sender_id, "Name: %s" % name)
        common.send_image(
            sender_id,
            player.get("profile").get("avatarfull"),
        )

        common.send_message(sender_id, "Let me find some insights about you")

        """Win Rate
        """
        wl = get_wl(account_id)
        total_matches = wl.get("lose") + wl.get("win")
        winrate = (wl.get("win") / float(total_matches)) * 100
        common.send_message(
            sender_id,
            "Winrate: %s" % winrate + "%"
        )
        common.send_message(sender_id, "That's great!!!")

        """Player statistics
        """
        common.send_message(
            sender_id,
            "I can help you calculate some statistics based on your %s matches:" % total_matches
        )
        player_stats = get_player_statistics(account_id)
        for index, value in player_stats.iteritems():
            common.send_message(
                sender_id,
                " -- %s: %s" % (index, value)
            )
        common.send_message(sender_id, "Hmm.. That's the average number you got per match. Keep it up!")
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
        statistics[item['field']] = item['sum'] / item['n']

    return statistics
