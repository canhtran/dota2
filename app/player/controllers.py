import os
import json
import dota2api
import config
from flask import Blueprint, request, render_template
from common import util, db
from bson.json_util import dumps

player = Blueprint('player', __name__, url_prefix='/player')

dota2api = dota2api.Initialise(config.STEAM_KEY)


@player.route('/')
def index():
    list_player = db.load_mongo('Dota2API', 'player_information')
    return render_template("player/index.html", data=list_player)


@player.route('/add', methods=['POST'])
def add():
    # account_id = 76561198067352481
    account_id = request.form['playersteamid']
    account32 = util.convertSteamAccount(account_id)
    player_info = dota2api.get_player_summaries(int(account_id))
    history = dota2api.get_match_history(account_id)
    first20 = history['matches'][:20]

    match20 = []
    for match in first20:
        match = dota2api.get_match_details(match['match_id'])
        match_player = [x for x in match['players'] if x['account_id'] == account32][0]
        match20.append(match_player)

    player_performance = {}
    player_performance['steamid'] = str(account_id)
    player_performance['match'] = match20

    # Save to Database
    re1 = db.save_line_by_line('Dota2API', player_performance, 'player_performance')
    re2 = db.save_line_by_line('Dota2API', player_info['players'][0], 'player_information')

    return 'done'


@player.route('/get/<steamid>')
def get(steamid):
    projection = {"match": 1, "_id": 0}
    query = {'steamid': str(steamid)}
    player_performance = db.load_match('Dota2API', 'player_performance', projection, query)
    player_performance = player_performance[0]['match']
    chart_data = []
    for i in player_performance:
        data = {}
        data['kills'] = i['kills']
        data['assists'] = i['assists']
        data['deaths'] = i['deaths']
        data['xp_per_min'] = i['xp_per_min']
        data['gold_per_min'] = i['gold_per_min']
        data['last_hits'] = i['last_hits']
        data['denies'] = i['denies']
        data['heroname'] = i['hero_name']
        chart_data.append(data)
        del data

    return dumps(chart_data)


@player.route('/detail/<steamid>')
def detail(steamid):
    projection = {"match": 1, "_id": 0}
    query = {'steamid': str(steamid)}
    player_performance = db.load_match('Dota2API', 'player_performance', projection, query)
    player_info = db.load_mongo('Dota2API', 'player_information', query)
    return render_template('player/detail.html', info = player_info)
