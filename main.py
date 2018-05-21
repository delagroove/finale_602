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

app = Flask(__name__)


@app.route('/')
def index():
    return doCorr()

@app.route('/corr2')
def index2():
    return doCorr2()

def correlation1():
    client = MongoClient(port=27017)
    db = client.final
    result = db.coins.find({'time': { '$gt' : 1506816000, '$lt':1514764800}, 'FROM': 'BTC', 'TO': 'BTS'})
    df = pd.DataFrame(list(result))
    #print(df.describe())
    print(df)
    print(df.corr())


def correlation2():
    client = MongoClient(port=27017)
    db = client.final
    result = db.coins.find({'time': { '$gt' : 1514764800, '$lt':1522540800}})
    print(json.dumps(list(result), sort_keys=True, indent=4, default=json_util.default))


def doCorr():
    client = MongoClient(port=27017)
    db = client.finals
    records = db.coins_usd.find({'time': { '$gt' : 1506816000, '$lt':1514764800}})
    recjson = dumps(records)
    #print(recjson)
    bjson = json.loads(recjson)
    dfret = pd.DataFrame(bjson)
    dfret.set_index('time')
    dfret = dfret.select(lambda col: col.find('close') > -1, axis=1)
    #dfret.filter(regex=("/close/"))
    dfcorr = dfret.corr()
    return dfcorr.to_json()

def doCorr2():
    client = MongoClient(port=27017)
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

if __name__ == "__main__":
    app.run(debug=True)
