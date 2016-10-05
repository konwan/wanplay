#!/usr/bin/env python
#coding=UTF-8

import os
import sys
sys.path.append("/data/migo/athena/lib")
from athena_variable import *
import sys
import pyspark
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext, Row
import datetime
import json
import ast
from operator import itemgetter
from pymongo import MongoClient
import requests
import logging


sys.path.append("/data/migo/athena/mode")
from conf import ApiConf


def ta_filter(line):
    if store == line[0].encode('utf-8') and type in line[2]:
        if tag1 != 0 and tag2 != 0 and tag3 != 0:
            if (int(line[12]) & tag1) and (int(line[13]) & tag2) and (int(line[14]) & tag3) :
                return line
        if tag1 != 0 and tag2 != 0 and tag3 == 0:
            if (int(line[12]) & tag1) and (int(line[13]) & tag2) :
                return line
        if tag1 != 0 and tag2 == 0 and tag3 != 0:
            if (int(line[12]) & tag1) and (int(line[14]) & tag3) :
                return line
        if tag1 == 0 and tag2 != 0 and tag3 != 0:
            if (int(line[13]) & tag2) and (int(line[14]) & tag3) :
                return line
        if tag1 != 0 and tag2 == 0 and tag3 == 0:
            if (int(line[12]) & tag1) :
                return line
        if tag1 == 0 and tag2 != 0 and tag3 == 0:
            if (int(line[13]) & tag2) :
                return line
        if tag1 == 0 and tag2 == 0 and tag3 != 0:
            if (int(line[14]) & tag3) :
                return line
        if tag1 == 0 and tag2 == 0 and tag3 == 0:
            return line
            
def npt_filter(line):
    if npt != 0 :
        if npt & int(2**0) and npt & (2**1) and npt & (2**2) :
            if (line[6] == "H" or line[6] == "M" or line[6] == "L"):
                return line
        if npt & int(2**0) and npt & (2**1) :
            if (line[6] == "H" or line[6] == "M"):
                return line
        if npt & int(2**0) and npt & (2**2) :
            if (line[6] == "H" or line[6] == "L"):
                return line
        if npt & (2**1) and npt & (2**2) :
            if (line[6] == "M" or line[6] == "L"):
                return line
        if npt & int(2**0) :
            if (line[6] == "H"):
                return line
        if npt & (2**1) :
            if (line[6] == "M"):
                return line
        if npt & (2**2) :
            if (line[6] == "L"):
                return line
    else :
        return line
                
def sep_bitmask(measure):
    tag = bin(int(measure))
    bitmask=[]
    for idx, val  in enumerate( tag[2:] ):
        if str(val) == "1" :
            bitmask.append( (2**((len(tag[2:])-1)-idx)) )
    return bitmask



def meb_partition(lists):
    result = []
    data_index = [0,1,3,4,5,6,12,11,13,19,20,21,7,8,9,2]

    for i in lists:
        line = [x for x in list( itemgetter(*data_index)( i.split("\t") ) )]
        if store == line[0].encode('utf-8') and type in line[2]:
            if channel == "1" :
                if line[9] != '' :
                    result.append(line)
            elif channel == "2" :
                if line[10] != '' :
                    result.append(line)
            elif channel == "3" :
                if line[11] != '' :
                    result.append(line)
            elif channel == "0" :
                result.append(line)
    return result
    
def npt_partitions(lists):
    result = []
    for line in lists:
        result.append( {"member":[x for x in list( itemgetter(*rs_index)(line) )]} )

    if countornot == "0":
        try:
            client = MongoClient(MIGO_MONGO_TA_URL)
            db = client['API_meb']
            collection = db[mlid]
            if len(result) != 0 :
                collection.insert( result )
            else :
                result = result
        except:
            collection.drop()
        finally:
            client.close()

    return result
    
if __name__ == "__main__":

    shop = sys.argv[1]
    store = revert_storeid(sys.argv[2])
    caldate = sys.argv[3]
    tag1 = int(sys.argv[4])
    tag2 = int(sys.argv[5])
    tag3 = int(sys.argv[6])
    type = sys.argv[7]
    npt = int(sys.argv[8])
    countornot = sys.argv[9]
    channel = sys.argv[10]
    mlid = sys.argv[11]


    api_logger = logging.getLogger('apilog')
    spark_hdlr = logging.FileHandler('/home/athena/api_spark.log')
    formatter = logging.Formatter('%(asctime)s  [%(name)s] [%(levelname)s] - %(message)s')
    spark_hdlr.setFormatter(formatter)

    api_logger.addHandler(spark_hdlr)
    api_logger.setLevel(logging.INFO)

    start_sp = datetime.datetime.now()
    mongo_tmp = 0


    ac = ApiConf('hdfs','cluster')
    pre_path = ac.getPath()
    meball = "{prepath}/{shop}/meb_attribute/{caldate}".format(prepath=pre_path, shop=shop, caldate=caldate)

    cf = SparkConf().setAppName("[API-test] {}-{}-{}-{}-{}-{}".format(store, caldate, tag1, tag2, tag3, npt)).set("spark.executor.memory" , "4g").set("spark.executor.instances", "10").set("spark.executor.cores", "4").set("spark.cores.max", "40")
    sc = SparkContext(conf = cf)

    result = { "key": mlid, "rows": -1 }
    
    try:
        data_index = [0,1,3,4,5,6,12,11,13,19,20,21,7,8,9,2]
        raw_meball = sc.textFile(meball, 100)\
                       .mapPartitions(meb_partition).cache()
        if not raw_meball.isEmpty() :
            ta_meb = raw_meball.filter(ta_filter).cache()
            if not ta_meb.isEmpty() > 0 :
                npt_meb = ta_meb.filter(npt_filter).cache()
                if not npt_meb.isEmpty() > 0:
                    if countornot == "1":
                        print npt_meb.count()
                    else :
                        client = MongoClient(MIGO_MONGO_TA_URL)
                        client['API_meb'][mlid].drop()
                        client.close()

                        rs_index = [1,3,4,5,6,7,8,9,10,11,15]
                        meb_list = npt_meb.coalesce(30).mapPartitions(npt_partitions).cache()
                        hdfs_cnt = meb_list.count()

                        client = MongoClient(MIGO_MONGO_TA_URL)
                        db = client['API_meb']
                        collection = db[mlid]
                        mongo_cnt = collection.count()

                        if hdfs_cnt == mongo_cnt :
                            result = {
                                "key": mlid,
                                "rows": hdfs_cnt
                            }
                        client.close()
                else :
                    mongo_cnt = -1
                    print "-1" # no npt
            else :
                mongo_cnt = -2
                print "-2" #no ta
        else :
            mongo_cnt = -3
            print "-3" # no meb
    except:
        mongo_cnt = -4
        print "-4" #no file

    sc.stop()


    end_sp = datetime.datetime.now()
    api_logger.info('[{}_{}_{}_{}_{}_{}] - spark take {} minutes, [{}] get {} mebs '.format(store, caldate, tag1, tag2, tag3, npt, ((end_sp - start_sp).seconds * 1.0) / 60.0, mlid, mongo_cnt))

    url = SHOPTELL_BK_CALLBACK
    response = requests.post(url, data=result)

    api_logger.info('api call status {}'.format(response.status_code))
