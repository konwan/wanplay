#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os
sys.path.append("/data/migo/athena/lib")

from athena_variable import *
import time, datetime as dt
from datetime import date, timedelta, datetime

import pymongo
from pymongo import MongoClient

class Pandora(object):
    def __init__(self, removejson, insertjson):
        self.removejson = removejson
        self.insertjson = insertjson

    def savemongo(self):
        #write_mongo = MongoClient(host="10.0.1.24:27017")
        #write_mongo = MongoClient(MIGO_MONGO_TA_URL)
        write_db = write_mongo["ProjectLogHistory_Athena"]
        write_db["ProcessAutomation"].remove(self.removejson)
        write_db["ProcessAutomation"].insert(self.insertjson)
        write_mongo.close()



class Mongo(object):
    def __init__(self, shopid, db, type, enddate):
        self.host = MIGO_MONGO_TA_URL
        self.shopid = shopid
        self.db = db
        self.type = type
        self.enddate = enddate
        #self.collection = collection
        self.start()
        self.end()

    def start(self):
        self.mc = MongoClient(self.host)
        #self.alldbs = self.mc.database_names()
        if self.type == "others" :
            self.checkothers()
        elif self.type == "ta" :
            self.checkta()
        else :
            print "choose others or ta"


    def checkta(self):
        write_db = self.mc[self.db]
        allcollections = write_db.collection_names()
        listdate = []
        losedays = []

        for i in allcollections :
            if "Member" in i :
                listdate.append(i[-8:])

        firstdate = min(listdate)

        d1 = datetime.strptime(firstdate, '%Y%m%d').date()
        d2 = datetime.strptime(self.enddate, '%Y%m%d').date()

        delta = d2 - d1
        for i in range(delta.days + 1):
            date = datetime.strftime((d1 + timedelta(days=i)), '%Y%m%d')
            if date not in listdate :
                losedays.append(date)

        print self.db + " for " + str(len(allcollections)) + " days ta"
        print self.db + " lose ta " + str(losedays)


    def checkothers(self):
        write_db = self.mc[self.db]
        #allcollections = write_db.collection_names()
        item = "Item_" + self.shopid
        member = "Member_" + self.shopid

        item_cnt = write_db[item].count()
        member_cnt = write_db[member].count()
        store_cnt = write_db["Store"].find({"ShopID" : self.shopid}).count()

        if (item not in allcollections) :
            print item + " is not exist "
        elif (item_cnt == 0) :
            print item + " has no count "
        else :
            print item + " => " + str(item_cnt)

        if (member not in allcollections) :
            print member + " is not exist "
        elif (member_cnt == 0) :
            print member + " has no count "
        else :
            print member + " => " + str(member_cnt)

        if (store_cnt == 0) :
            print " Store has no count "
        else :
            print self.shopid + " store => " + str(store_cnt)

        #write_db[self.db].remove(self.removejson)
        #write_db[self.db].insert(self.insertjson)

    def end(self):
        self.mc.close()


if __name__ == '__main__':

    #python cindy/others.py "mentor" "ProjectTagInfo_mentor" "ta" "20150618"

    if len(sys.argv) != 5 :
        print "not enough argument, should set [shop_id, collection_name, check_type, ta_enddate]"
    else :
        Mongo(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


    #Mongo("mentor", "ProjectBasicInfo", "others", "")
    #Mongo("mentor", "ProjectTagInfo_mentor", "ta", "20150618")
