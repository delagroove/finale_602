#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import requests
import json
import types
import pandas as pd
from bson import json_util
from collections import namedtuple
from ast import literal_eval
import numpy as np
from bson import json_util
from bson.json_util import dumps
from flask import Flask, render_template
from flask import request
from datetime import datetime
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return getTop15ByMarketCap()

@app.route('/top15bymc')
def Analysis1():
    return getTop15ByMarketCap()

@app.route('/top15byhvol')
def Analysis3():
    return getTop15ByHistoricalVol()

@app.route('/getrcorr/<pair>')
def Analysis2(pair=None):
    return getRollingCorr(pair)

def GetMongoClient():
    client = MongoClient('mongodb://mongo:27017')
    #client = MongoClient(port=27017)
    return client

def correlation1():
    client = GetMongoClient()
    db = client.final
    result = db.coins.find({'time': { '$gt' : 1506816000, '$lt':1514764800}, 'FROM': 'BTC', 'TO': 'BTS'})
    df = pd.DataFrame(list(result))
    #print(df.describe())
    print(df)
    print(df.corr())

def correlation2():
    client = GetMongoClient()
    db = client.final
    result = db.coins.find({'time': { '$gt' : 1514764800, '$lt':1522540800}})
    print(json.dumps(list(result), sort_keys=True, indent=4, default=json_util.default))


def getData():
    client = GetMongoClient()
    db = client.finals
    records = db.coins_usd.find({'time': { '$gt' : 1506816000, '$lt':1514764800}})
    db.close
    recjson = dumps(records)
    bjson = json.loads(recjson)
    dfret = pd.DataFrame(bjson)

    #dfret = dfret.select(lambda col: col.find('close') > -1, axis=1)
    return dfret


def getDataPeriod(start, end):
    client = GetMongoClient()
    db = client.finals
    records = db.coins_usd.find({'time': { '$gt' : start, '$lt':end}})
    db.close
    recjson = dumps(records)
    bjson = json.loads(recjson)
    dfret = pd.DataFrame(bjson)
    return dfret

def doCorr2():
    client = GetMongoClient()
    db = client.finals
    records = db.coins_usd.find({'time': { '$gt' : 1514764800, '$lt':1522540800}})
    recjson = dumps(records)
    #print(recjson)
    bjson = json.loads(recjson)
    dfret = pd.DataFrame(bjson)
    dfret.set_index('time')
    dfret = dfret.select(lambda col: col.find('close') > -1, axis=1)
    #dfret.filter(regex=("/close/"))
    dfcorr = dfret.corr()
    return dfcorr.to_json()

def getTop15ByMarketCap():
    client = GetMongoClient()
    db = client.finals
    db.close

    records = db.currencies.find({'rank': {'$lt': 20}})#.sort([{'rank':1}])
    recjson = dumps(records)
    bjson = json.loads(recjson)
    dfret = pd.DataFrame(bjson)

    currlist = (dfret.sort_values(by=['rank'])["symbol"])
    cols = []
    rencols = []
    for curr in currlist:
        cols.append(curr+"_"+"close")
        rencols.append(curr)

    dfData = getData()
    dfset = dfData[cols]
    dfset.colums = rencols
    dfret = dfset.corr()
    dfret = dfret.round(2)
    return dfret.to_json()

def getRollingCorr(pair):
    cols=[]
    if pair== None:
        arrpair = "BTC-ETH".split("-")
    else:
        arrpair = pair.split("-")

    cols=[arrpair[0]+"_close", arrpair[1]+"_close"]
    rencols = [arrpair[0], arrpair[1]]

    dfData = getData()
    dfset = dfData[cols]
    dfset.columns = rencols
    psret = pd.rolling_corr(dfset[arrpair[0]],dfset[arrpair[1]],20)
    dfret = pd.DataFrame({'idx': dfData["time"], 'rcorr': psret.values})
    dfret = pd.DataFrame(dfret.loc[dfret['rcorr'] > 0 ])
    dfret = dfret.round(2)
    #return dfret[~dfret.isnull()].to_json()
    #return dfret.to_json()
    return dfret.to_json()

def getTop15ByHistoricalVol():
    client = GetMongoClient()
    db = client.finals
    db.close

    records = db.currencies.find({'rank': {'$lt': 100}})#.sort([{'rank':1}])
    recjson = dumps(records)
    bjson = json.loads(recjson)
    dfret = pd.DataFrame(bjson)

    dt = datetime.today().date()
    tstamp = time.mktime(dt.timetuple())
    currts = int(datetime.fromtimestamp(tstamp).timestamp())

    currlist = (dfret.sort_values(by=['rank'])["symbol"])
    cols = []
    for curr in currlist:
        cols.append(curr+"_"+"close")

    dfData = getDataPeriod(currts - 86400*30, currts)
    dfset = dfData[cols]

    dfset = dfset.pct_change()
    ps = dfset.agg('std')
    psresult = ps.apply(lambda x: x * np.sqrt(365)).sort_values(ascending=False)

    j = 0
    top15byvol = []
    rencols = []
    for ticker in psresult.index:
        if(j < 15):
            top15byvol.append(ticker)
            rencols.append(ticker.replace("_close", ""))
        j = j + 1

    dfset = dfData[top15byvol]
    dfset.columns= rencols
    dfret = dfset.corr()
    dfret = dfret.round(2)
    return dfret.to_json()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

#getTop15ByMarketCap()
#getTop15ByHistoricalVol()
