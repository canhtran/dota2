import requests
import pandas as pd

OPENDOTA_ENDPOINT = 'https://api.opendota.com/api/'

def call_opendata(path, params=None):
    return requests.get(OPENDOTA_ENDPOINT + path, params=params).json()

proPlayers = call_opendata("proPlayers")
print(len(proPlayers))
