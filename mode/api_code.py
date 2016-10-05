from django.shortcuts import render
from django import http
from django.core import serializers
from django.utils.text import compress_string
from bson import json_util

import ast
import copy
import re
import json
import datetime, time

import os
import sys
sys.path.append("/data/migo/athena/lib")
from athena_variable import *
import subprocess
from . import cleaner_q
from cleaner_q import storeid_cleaner

class Ac():
    ac = ApiConf('hdfs','cluster')
    hdfs_mode = ac.hdfs_mode

def _response(data, is_encoded):
    if not is_encoded:
        data = json.dumps(data, ensure_ascii="False")

    response = http.HttpResponse(data)
    response.__setitem__("Content-type", "application/json; charset=utf-8")
    response.__setitem__("Access-Control-Allow-Origin", "*")
    response.__setitem__("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS")
    response.__setitem__("Access-Control-Allow-Headers", "*")

    return response
    #return http.HttpResponse(data, content_type="application/json; charset=utf-8")


def test(request, shopid, storeid, caldate, type, tag1, tag2, tag3, npt, countornot, channel, mebid):
    is_encoded = False
    meball = {
        "shop_id" : shopid,
        "store_id" : storeid,
        "caldate" : caldate,
        "type" : type,
        "tag1" : tag1,
        "tag2" : tag2,
        "tag3" : tag3,
        "npt"  : npt,
        "channel" : channel
    }

    prog = "/data/migo/athena/lib/util/get_xxxxxxx_log.py"
    if Ac.hdfs_mode == "single":
          cmd = "python {} {} {} {} {} {} {} {} {} {} {} {}".format( prog, shopid, storeid_cleaner(storeid, True, 'utf-8'), caldate.replace("-",""), tag1, tag2, tag3, type, npt, countornot, channel, mebid)
    else :
          cmd = "ssh athena@{} python {} {} {} {} {} {} {} {} {} {} {} {}".format(MIGO_SPARK_MASTER, prog, shopid, storeid_cleaner(storeid, True, 'utf-8'), caldate.replace("-",""), tag1, tag2, tag3, type, npt, countornot, channel, mebid)

    if countornot == "0" :
        meball["msg"] = "{} get request".format(mebid)
        subprocess.Popen(cmd, shell=True)
    else :
        rs = os.popen(cmd).read().strip()
        result = ast.literal_eval(rs)
        if result < 0 :
            result_cnt = 0
        else :
            result_cnt = result
        meball["count"] = result_cnt
    return _response(meball, is_encoded)
