#!/usr/bin/env python
#coding=UTF-8
import sys
sys.path.append("/data/migo/athena/lib")

from athena_variable import *
import pyspark
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
import datetime
import json
from operator import itemgetter
import pymongo
from pymongo import MongoClient

class Mongo(object):
    def __init__(self, shopid,  caldate, enddate):
        self.host = MIGO_MONGO_TA_URL
        self.shopid = shopid
        self.db = "ProjectReport_StarterDIY"
        self.caldate = caldate
        self.enddate = enddate
        #self.condition = {}
        self.start()

    def start(self):
        self.mc = MongoClient(self.host)

    def getdata(self, type):
        if type == 1 :
            self.collection = "DIYReportG"
            #self.condition = {"StoreID": self.shopid, "CalDate":datetime.datetime(2016, 3, 10) }
            self.condition = {"CalDate":{"$gte": datetime.datetime.strptime(self.caldate, "%Y%m%d"), "$lte": datetime.datetime.strptime(self.enddate, "%Y%m%d")}}
            #created_at: {
            #    $gte: ISODate("2010-04-29T00:00:00.000Z"),
            #    $lt: ISODate("2010-05-01T00:00:00.000Z")
            #}

        else :
            self.collection = "DIYReport"
            #self.condition = {"CalDate":{"$gt": datetime.datetime.strptime(self.caldate, "%Y%m%d")}}
            self.condition = {"CalDate":{"$gte": datetime.datetime.strptime(self.caldate, "%Y%m%d"), "$lte": datetime.datetime.strptime(self.enddate, "%Y%m%d")}}

        write_db = self.mc[self.db]
        result = write_db[self.collection].find(self.condition)#{"StoreID": self.shopid, "CalDate":datetime.datetime.strptime(self.caldate, "%Y%m%d") })#datetime.datetime(2016, 4, 10) })
        return result

    def end(self):
        self.mc.close()
        
        

if __name__ == "__main__":
    shop = sys.argv[1]
    caldate = sys.argv[2]
    enddate = sys.argv[3]

    m = Mongo(shop, caldate, enddate)
    fm = m.getdata(1)
    nes = m.getdata(0)

fm_index = [0,2,1,6,8,7]  #FH, FL, FM, LH, LL, LM, MH, ML, MM, RH, RL, RM
m.end()

print "end off getting data from mongo"

split_key = "@@@"
fm_empty = [""] * (5 * 6)


cf = SparkConf().setAppName("[star-{}-{}]".format(shop, caldate)).set("spark.executor.memory", "5g")
sc = SparkContext(conf = cf)

raw_fm = sc.parallelize(fm, 100).map(lambda x: ("{}{sep}{}{sep}{}".format(x["CalDate"].strftime("%Y%m%d"),x["PeriodType"], x["StoreID"].encode("utf-8"), sep=split_key), [x["Count"]["N"][a] for a in itemgetter(*fm_index)(sorted(x["Count"]["N"].keys())) ] + [x["Count"]["E0"][a] for a in itemgetter(*fm_index)(sorted(x["Count"]["E0"].keys())) ] + [x["Count"]["S1"][a] for a in itemgetter(*fm_index)(sorted(x["Count"]["S1"].keys())) ] + [x["Count"]["S2"][a] for a in itemgetter(*fm_index)(sorted(x["Count"]["S2"].keys())) ] + [x["Count"]["S3"][a] for a in itemgetter(*fm_index)(sorted(x["Count"]["S3"].keys())) ] )).cache()

raw_nes = sc.parallelize(nes, 100).map(lambda y: ("{}{sep}{}{sep}{}".format(y["CalDate"].strftime("%Y%m%d"), y["PeriodType"], y["StoreID"].encode("utf-8"), sep=split_key), y["PeriodRecords"]["ValidChangeNumber"] + [y["PeriodRecords"]["AddedRate"][0], y["PeriodRecords"]["AddedRate"][1], y["PeriodRecords"]["ChurnRate"][4], y["PeriodRecords"]["ConversionRate"][0], y["PeriodRecords"]["Active"][1], y["PeriodRecords"]["WakeUpRate"][2], y["PeriodRecords"]["WakeUpRate"][3], y["PeriodRecords"]["WakeUpRate"][4], y["PeriodRecords"]["ARPU"][0], y["PeriodRecords"]["ARPU"][1] ])).cache()


nf = raw_nes.leftOuterJoin(raw_fm)\
            .map(lambda x : (x[0].split(split_key) + x[1][0] + x[1][1]) if x[1][1] is not None else (x[0].split(split_key) + x[1][0] + fm_empty))\
            .map(lambda x : ",".join("\"" + str(d) +"\"" for d in x) )
            #.map(lambda x : ",".join("\"" + str(d) +"\"" for d in x))
#print ','.join("\"" + str(d) +"\"" for d in nf.collect())

f = open("star_{}.csv".format(enddate),"w")
for i in nf.collect() :
    print >> f, i

#nf.saveAsTextFile("file:///root/star")

#print "nes count " + str(raw_nes.count())
#print "fm count " + str(raw_fm.count())
print nf.take(2)

#print nf.collect()

sc.stop()
