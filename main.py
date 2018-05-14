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


def correlation1():
    client = MongoClient(port=27017)
    db = client.final
    result = db.coins.find({'time': { '$gt' : 1506816000, '$lt':1514764800}})
    print(json.dumps(list(result), sort_keys=True, indent=4, default=json_util.default))


def correlation2():
    client = MongoClient(port=27017)
    db = client.final
    result = db.coins.find({'time': { '$gt' : 1514764800, '$lt':1522540800}})
    print(json.dumps(list(result), sort_keys=True, indent=4, default=json_util.default))

# 1506816000 -> october 1st 2017 00:00UTC
# 1514764800 jan 1 2018 00:00UTC
# 1522540800 April 1, 2018 00:00 UTC
correlation1()
