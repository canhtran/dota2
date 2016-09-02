import os
import json
from flask import Blueprint, request, render_template
from common import util, db

main = Blueprint('main', __name__)


# Homepage
# Need to load all the list 2 times due to the limitation of Jinja
@main.route('/')
def index():
    list_player = db.load_mongo('Dota2API', 'player_information')
    l = db.load_mongo('Dota2API', 'player_information')
    return render_template("homepage/index.html", data = list_player, test=l)