import requests
import json
from bson import json_util
from collections import namedtuple
from pymongo import MongoClient
import itertools
from bson.json_util import dumps
from datetime import datetime
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
db = None

class CryptoDBUtil():

    def __init__(self):
        pass

    def coinFiatList(self):
        print(datetime.now())
        client = MongoClient(port=27017)
        db = client.finals

        rec = db.coins.find()
        if rec.count() > 0:
            print("Removing existing collection..")
            db.drop_collection('coins_usd')
            db.drop_collection('currencies')

        dfCoinlist = pd.DataFrame()
        currrec = db.tickerlist.find()
        if (currrec.count() > 0):
            recjson = dumps(currrec)
            bjson = json.loads(recjson)
            dfCoinlist = pd.DataFrame(bjson)
        else:
            dfResult = pd.DataFrame()
            url = "https://api.coinmarketcap.com/v1/ticker/"
            dfCoinlist = pd.read_json(url)

        newlist = dfCoinlist.loc[dfCoinlist['rank'] < 100].sort_values(by=['rank'])["symbol"]
        print(newlist)
        records = json.loads(dfCoinlist.T.to_json()).values()
        if (currrec.count() == 0):
            db.tickerlist.insert(records)

        currencies = []
        curr_with_data = []
        for item in newlist:
            currencies.append(item)

        urls = []
        for currency in currencies:
            urls.append("https://min-api.cryptocompare.com/data/histoday?fsym=" + currency + "&tsym=USD&limit=730")

        pool = ThreadPool(13)
        results = pool.map(requests.get, urls)
        pool.close()
        pool.join()

        n = 0
        for result in results:
            if len(result.json()['Data']) > 0:
                df = pd.DataFrame(result.json()['Data'])
                #df = df.loc[df['close'] > 0]
                df1 = df[['time', 'open', 'close', 'volumeto', 'volumefrom']]
                df1.columns = ['time', currencies[n] + "_open", currencies[n] + "_close", currencies[n] + '_volumeto',
                               currencies[n] + "_volumefrom"]
                if n == 0:
                    dfResult = df1
                else:
                    dfResult = pd.merge(dfResult, df1, how='inner', on='time')
                curr_with_data.append([currencies[n],n])
                df1.to_csv("c:\\temp\\dfcsv\\" + currencies[n] + ".csv")
                print("Processed..." + currencies[n] + ":" + str(n) + ":" + str(len(result.json()['Data'])))
            else:
                print("Error processing..." + currencies[n] + ":" + str(n) + ":" + str(len(result.json()['Data'])))
            n = n + 1

        records = json.loads(dfResult.T.to_json()).values()
        db.coins_usd.insert(records)

        dfcurr = pd.DataFrame(curr_with_data)
        dfcurr.columns = ['symbol', 'rank']
        records = json.loads(dfcurr.T.to_json()).values()
        db.currencies.insert(records)

        return True

cobj = CryptoDBUtil()
cobj.coinFiatList()
