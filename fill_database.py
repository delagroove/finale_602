import requests
import json
from bson import json_util
from collections import namedtuple
from pymongo import MongoClient
import itertools
from bson.json_util import dumps
from datetime import datetime
import pandas as pd
db = None

class CryptoDBUtil():

    def __init__(self):
        pass

    def coinList(self):
        print(datetime.now())
        client = MongoClient(port=27017)
        db = client.finals

        rec = db.coins.find()
        if rec.count() > 0:
            db.drop_collection('coins')

        dfResult = pd.DataFrame()
        res = requests.get('https://min-api.cryptocompare.com/data/all/coinlist')
        res_json = [x for x in res.json()['Data'].values() if int(x['SortOrder']) < 15]
        newlist = sorted(res_json, key=lambda k: k['SortOrder'])
        currencies = []
        for item in newlist:
            print("Removing existing collection..")
            currencies.append(item['Name'])
        #print(currencies)

        pairs = list(itertools.combinations(currencies, 2))
        i = 0
        for pair in pairs:
            print("processing..." + pair[0] + "-" + pair[1])
            res = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym="+pair[0]+"&tsym="+pair[1]+"&limit=730")
            df = pd.DataFrame(res.json()['Data'])
            df1 = df[['time', 'close']]
            df1.columns = ['time', pair[0] + "-" + pair[1]]
            if i==0:
                dfResult = df1
                i = i + 1  #not required after i > 0
            else:
                dfResult = pd.merge(dfResult, df1, how='inner', on='time')
        records = json.loads(dfResult.T.to_json()).values()
        db.coins.insert(records)
        print(datetime.now())
        return True


cobj = CryptoDBUtil()
cobj.coinList()

