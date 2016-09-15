import os
import json
import dota2api
import config
from flask import Blueprint, request, render_template
from common import util, db
from bson.json_util import dumps
import time

player = Blueprint('player', __name__, url_prefix='/player')

api = dota2api.Initialise(config.STEAM_KEY)


# Temporary page which list all players
# Output: the cursor of list of players
@player.route('/')
def index():
  list_player = db.load_mongo('Dota2API', 'player_information')
  return render_template("player/index.html", data=list_player)


# Add player to database
# Process to get the data from API then save to mongodb
@player.route('/add', methods=['POST', 'GET'])
def add():
  account_id = request.form['playersteamid']
  print(account_id)
  account32 = util.convertSteamAccount(account_id)
  player_info = api.get_player_summaries(int(account_id))

  try:
    history = api.get_match_history(account_id)
    first20 = history['matches'][:20]
    match20 = []
    for match in first20:
      match = api.get_match_details(match['match_id'])
      match_player = [x for x in match['players'] if x['account_id'] == account32][0]
      match_player['time'] = match['start_time']
      match20.append(match_player)

    player_performance = {'steamid': str(account_id), 'match': match20}

    # Save to Database
    db.save_line_by_line('Dota2API', player_performance, 'player_performance')
    db.save_line_by_line('Dota2API', player_info['players'][0], 'player_information')
    return 'done'
  except:
    return 'This profile is private, please choose another one'


# Function for Ajax to get from Mongodb, re-format and send back as json
@player.route('/get/<steamid>')
def get(steamid):
  projection = {"match": 1, "_id": 0}
  query = {'steamid': str(steamid)}
  player_performance = db.load_match('Dota2API', 'player_performance', projection, query)
  player_performance = player_performance[0]['match']
  chart_data = []
  for i in player_performance:
    data = {'kills': i['kills'], 'assists': i['assists'], 'deaths': i['deaths'], 'xp_per_min': i['xp_per_min'],
            'gold_per_min': i['gold_per_min'], 'last_hits': i['last_hits'], 'denies': i['denies'],
            'heroname': i['hero_name']}
    chart_data.append(data)
    del data

  return dumps(chart_data)


# Player Details page
@player.route('/detail/<steamid>')
def detail(steamid):
  projection = {"match": 1, "_id": 0}
  query = {'steamid': str(steamid)}

  player_info = db.load_mongo('Dota2API', 'player_information', query)
  player_performance = db.load_match('Dota2API', 'player_performance', projection, query)
  player_performance = player_performance[0]['match']

  last_hits = 0
  denies = 0
  gold_spent = 0
  avg_lv = 0
  kills = 0
  deaths = 0
  assists = 0
  gold_per_min = 0
  xp_per_min = 0

  for match in player_performance:
    last_hits = last_hits + match['last_hits']
    denies = denies + match['denies']
    gold_spent = gold_spent + match['gold_spent']
    avg_lv = avg_lv + len(match['ability_upgrades'])
    kills = kills + match['kills']
    deaths = deaths + match['deaths']
    assists = assists + match['assists']
    gold_per_min = gold_per_min + match['gold_per_min']
    xp_per_min = xp_per_min + match['xp_per_min']

  return render_template('player/detail.html',
                         info=player_info,
                         last_hits=last_hits/20,
                         denies=denies/20,
                         gold_spent=gold_spent/20,
                         avg_lv=avg_lv/20,
                         kills=kills/20,
                         deaths=deaths/20,
                         assists=assists/20,
                         gold_per_min=gold_per_min/20,
                         xp_per_min=xp_per_min/20)


@player.route('/get/radar/<steamid>')
def getradar(steamid):
  projection = {"match": 1, "_id": 0}
  query = {'steamid': str(steamid)}
  player_performance = db.load_match('Dota2API', 'player_performance', projection, query)
  player_performance = player_performance[0]['match']
  chart_data = []

  last_hits = 0
  gold_spent = 0
  kills = 0
  deaths = 0
  assists = 0
  gold_per_min = 0
  heroes = []

  for match in player_performance:
    last_hits = last_hits + match['last_hits']
    gold_spent = gold_spent + match['gold_spent']
    kills = kills + match['kills']
    deaths = deaths + match['deaths']
    assists = assists + match['assists']
    gold_per_min = gold_per_min + match['gold_per_min']
    heroes.append(match['hero_id'])

  versatility = len(list(set(heroes))) * 5
  return dumps(versatility)