import requests
import pandas as pd

OPENDOTA_ENDPOINT = 'https://api.opendota.com/api/'

def call_opendata(path, params=None):
    return requests.get(OPENDOTA_ENDPOINT + path, params=params).json()

def get_player_heroes(account_id):
    return [h for h in call_opendata("/players/%s/heroes" % account_id) if h.get("games") > 0]

def get_heroes_hash(heroes):
    h = {}
    for hero in heroes:
        h[hero.get("id")] = hero
    return h

def get_player(account_id):
    return call_opendata("/players/" + account_id)

def get_player_statistics(account_id):
    totals = call_opendata("/players/" + account_id + "/totals")
    statistics = {}
    for item in totals[:8]:
        if item['n'] == 0:
            return False
        statistics[item['field']] = round(item['sum'] / item['n'])

    return statistics

if __name__ == '__main__':
    proPlayers = call_opendata("proPlayers")
    all_heroes = pd.read_csv("data/heroes.csv")

    heroes = []
    for index, row in all_heroes.iterrows():
        hero = {}
        hero["id"] = row["id"]
        hero["localized_name"] = row["localized_name"]
        hero["main_role"] = row["main_role"]
        heroes.append(hero)

    heroes_hash = get_heroes_hash(heroes)
    for player in proPlayers[400:1000]:
        if get_player(str(player['account_id'])).get('profile'):
            print("account_id: " + str(player['account_id']))
            player_stats = get_player_statistics(str(player['account_id']))
            if player_stats:
                print("account has stats" + str(player["account_id"]))
                for index, value in player_stats.items():
                    player[index] = value

            player_heroes = get_player_heroes(str(player['account_id']))
            if player_heroes:
                print(int(player_heroes[0]['hero_id']))
                player['main_role'] = heroes_hash[int(player_heroes[0]['hero_id'])].get("main_role")
        else:
            print("Don't have account " + str(player['account_id']))

    df = pd.DataFrame(proPlayers)
    df.to_csv("data/train400.csv" ,index=False)
