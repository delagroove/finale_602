import requests
import json
from bson import json_util
from collections import namedtuple
from pymongo import MongoClient
import itertools

db = None



def coinList():
    res = requests.get('https://min-api.cryptocompare.com/data/all/coinlist')
    res_json = [x for x in res.json()['Data'].values() if int(x['SortOrder']) < 15]
    newlist = sorted(res_json, key=lambda k: k['SortOrder'])
    currencies = []
    for item in newlist:
        currencies.append(item['Name'])
    #print(currencies)
    pairs = list(itertools.combinations(currencies, 2))
    for pair in pairs:
        res = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym="+pair[0]+"&tsym="+pair[1]+"&limit=730")
        result = json.loads(res.text)
        client = MongoClient(port=27017)
        db = client.final
        for item in result['Data']:
            result = db.coins.update_one({"FROM": pair[0], "TO": pair[1], 'time': item.get('time')},
            {'$set': {'close': item.get('close'),
            'high': item.get('high'),
            'low': item.get('low'),
            'open': item.get('open'),
            'volumefrom': item.get('volumefrom'),
            'volumeto': item.get('volumeto')}}, True)


coinList()
