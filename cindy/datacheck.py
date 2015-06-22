#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os, getpass
sys.path.append("/data/migo/athena/lib")
from athena_variable import *

import time, datetime as dt
from datetime import date, timedelta, datetime

import copy
import urllib, urllib2
try:
    import jsonlib2 as json
except:
    import json

import commands
import zipfile

#import pymongo
#from pymongo import MongoClient

class DataCheck(object) :
    def __init__(self, shop_id, checkftp, checkhadoop, checkmark, checkHis, checkInc, checkformat, checkdealdate, checkdealdetail, error_print_cnt) :
        self.shop_id = shop_id
        self.checkftp, self.checkhadoop = checkftp, checkhadoop
        self.checkmark, self.checkHis, self.checkInc = checkmark, checkHis, checkInc
        self.checkformat, self.checkdealdate, self.checkdealdetail = checkformat, checkdealdate, checkdealdetail
        self.error_print_cnt = error_print_cnt
        self.datatype, self.now_dir, self.now_filename, self.tmpfile = "", "", "", ""
        self.tmpline = ""

        self.customer_cnt, self.noncustomer_cnt = 0, 0
        self.score, self.dir_score = 0, 0       
        self.error_msg, self.final_msg = "", ""
        self.error_msg_mongo = {
             "file": self.now_filename,
             "format":{"schema":[], "empty":[], "specialchar":[], "date":[], "others":[] },
             "detail":{"losedays":"", "nofiledate":"", "notonlyfiledate":"","filedatenotmatch":"", "noncustomer":[]}
        }

        self.error_msg_dir_mongo = {
             "shop": self.shop_id,
             "folder": self.now_dir,
             "overall": {
                 "path":{ "dir":"", "file":"" },
                 "mark":{ "historical":[], "incremental":[]}
             },
             "data":[]
        }
        self.overalldata = {}
        self.overalldealdate = {
             "daterange": set(),
             "losedays": set()
        }
        self.customer_deal_type = {}

        # data upload source
        #self.ftp_src_path = "/data/diy-data/" + shop_id + "/upload"
        self.ftp_src_path = "/data/diy-data/" + shop_id + "/upload"
        self.ftp_src_dir = ["header","transaction","item","store","member"]
        self.ftp_src_file_type = [".csv", ".zip", ".txt"]
        self.ftp_mark_file_type = {"historical":".full", "incremental":".done"}

        self.date_error_t, self.date_error_len, self.data_error_cnt, self.data_error_empty, self.data_error_special_char = 0, 0, 0, 0, 0    
        self.data_set_date,self.data_dict_date = set(), {}
        self.dealfirstday, self.deallastday = "", ""

        #hadoop files
        self.hadoop_path = "/user/athena/"
        self.client = "ablejeans"
        self.hadoop_result_dir = ["activeness_month","activeness_week","valid_month","valid_week","wakeup_month","wakeup_week","arpu_month","arpu_week","conversion_month","conversion_week",
                                  "aggregation","lrfm","nes_lrfm_week", "nlp_week","ta",
                                  "data_prepare_item","data_prepare_member","data_prepare_recommendatin","adjusted_interval","incremental_interval","mu2_interval","mu_interval",
                                  "item_month","item_week","member_week","member_month","revenue_month","revenue_week","nes_member_month","nes_member_week","nes_tag_month","nes_tag_week"]
        
        self.exclude_char = ["!","@","#","$","%","^","&","*","~","?","_"]
        self.task_name = self.__class__.__name__ 
        self.status, self.url, self.src, self.dest = "", "", "", ""
        self.start_time, self.end_time = "", ""
        self.count_success, self.count_failed = 0, 0
       
    def savemongo(self, insertjson):
        write_mongo = MongoClient(MIGO_MONGO_TA_URL)
        write_db = write_mongo["ProjectLogHistory_Athena"]
        write_db["ETLHistory"].insert(insertjson)
        write_mongo.close()
 
    def savemongoapi(self) :
        try:
            urllib2.urlopen(self.url)
        except Exception as e:
            import logging.handlers

            my_logger = logging.getLogger('AthenaLogger')
            handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_LOCAL6, address="/dev/log")
            formatter = logging.Formatter('[%(name)s] [%(levelname)s] - %(message)s')
            handler.setFormatter(formatter)
            my_logger.addHandler(handler)
            my_logger.warn("Failure{err} in sending monitor request - {url}".format(err=str(e), url=self.url))

    def setdirdefault(self) :
        self.start_time, self.end_time = "", ""
        self.count_success, self.count_failed = 0, 0
        self.overalldata = {}
        self.customer_deal_type = {}
        self.error_msg_dir_mongo = {
             "folder": self.now_dir,
             "overall": {
                  "path":{ "dir":"", "file":"" },
                  "mark":{ "historical":[], "incremental":[]}
             },
             "data":[]
        }

    def setfiledefault(self) :
        self.score, self.customer_cnt, self.noncustomer_cnt = 0, 0, 0
        self.date_error_t, self.date_error_len, self.data_error_cnt, self.data_error_empty, self.data_error_special_char = 0, 0, 0, 0, 0
        self.data_set_date = set()
        self.data_dict_date = {}
        self.dealfirstday, self.deallastday = "", ""
        self.status, self.url, self.src, self.dest = "", "", "", ""
        self.error_msg_mongo = {
             "file":self.now_filename ,
             "format":{"schema":[], "empty":[], "specialchar":[], "date":[], "others":[] },
             "detail":{"losedays":"", "nofiledate":"", "notonlyfiledate":"","filedatenotmatch":"", "noncustomer":[]}
        }

        self.overalldealdate = {
             "daterange": set(),
             "losedays": set()
        }

    def dealdatelose(self) :
        losedays = []
        d1 = datetime.strptime(self.dealfirstday, '%Y-%m-%d').date()
        d2 = datetime.strptime(self.deallastday, '%Y-%m-%d').date()

        delta = d2 - d1
        for i in range(delta.days + 1):
            date = datetime.strftime((d1 + timedelta(days=i)), '%Y-%m-%d')
            if date not in self.data_dict_date.keys() :
                losedays.append(date)
        return losedays

    def dealdetail(self, filedate) :
        for i in self.data_set_date :
            if i[0] not in self.data_dict_date.keys() :
                self.data_dict_date[i[0]] = []
            self.data_dict_date[i[0]].append(i[1])

        if self.now_dir == "header" :
            if self.tmpfile not in self.customer_deal_type.keys() :
                self.customer_deal_type[self.tmpfile] = [self.customer_cnt, self.noncustomer_cnt]
            else :
                self.customer_deal_type[self.tmpfile] = [(self.customer_deal_type[self.tmpfile][0] + self.customer_cnt), (self.customer_deal_type[self.tmpfile][1] + self.noncustomer_cnt)]

            for i in sorted(self.data_dict_date.keys()) :
                if len(self.data_dict_date[i]) < 2 and "-999" not in self.data_dict_date[i] :
                    self.error_msg += "[data" + " - " + self.now_dir + "] - " + self.now_filename + " [" + i + "] only have noncustomer data \n"
                    self.error_msg_mongo["detail"]["noncustomer"].append(i)
                    self.score += -1

        if filedate not in self.data_dict_date.keys() :
            self.error_msg += "[data" + " - " + self.now_dir + "] - " + self.now_filename + " no [" + filedate + "] data in the file \n"
            self.error_msg_mongo["detail"]["nofiledate"] = (" no [" + filedate + "] data ")
            self.score += -1

        self.dealfirstday, self.deallastday = min(self.data_dict_date.keys()), max(self.data_dict_date.keys())
        if self.datatype == "incremental" :
            if len(self.data_dict_date.keys()) > 1 :
                self.error_msg += "[data" + " - " + self.now_dir + "] - " + self.now_filename + " not only [" + filedate + "] data \n"
                self.error_msg_mongo["detail"]["notonlyfiledate"] = (" not only [" + filedate + "] data ")
                self.score += -1
            if self.dealfirstday != self.deallastday :
                self.error_msg += "[final" + " - " + self.now_dir + "] - " + self.now_filename + " deal date is between [ " + self.dealfirstday + " ~ " + self.deallastday + " ]\n"
                self.error_msg_mongo["detail"]["filedatenotmatch"] = (" deal date is between " + self.dealfirstday + " ~ " + self.deallastday )
        else :            
            losedays = self.dealdatelose()
            losedayscnt = len(losedays)
            if losedayscnt != 0 :
                self.error_msg += "[final" + " - " + self.now_dir + "] - " + self.now_filename + " lose " +str(losedayscnt) + " days data ====> \n" + str(losedays) + "\n"
                self.error_msg_mongo["detail"]["losedays"] = str(losedays)
                self.score += -1     
                self.overalldealdate["losedays"] |= set(losedays)
            self.overalldealdate["daterange"].add(self.dealfirstday)
            self.overalldealdate["daterange"].add(self.deallastday)
  
            if self.tmpfile not in self.overalldata.keys() :
                self.overalldata[self.tmpfile] = self.overalldealdate.copy()
            else :
                self.overalldata[self.tmpfile]["daterange"].add(self.dealfirstday)
                self.overalldata[self.tmpfile]["daterange"].add(self.deallastday)
                self.overalldata[self.tmpfile]["losedays"] |= set(losedays)

    def dataspec(self, standcolcnt, colcnt) :
        if standcolcnt != colcnt :
            self.data_error_cnt += 1
            if self.data_error_cnt <= self.error_print_cnt :
                self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " wrong schema != " + str(colcnt) + " ==> " + str(self.tmpline).decode('string_escape') + "\n"
                self.error_msg_mongo["format"]["schema"].append(self.tmpline)
            self.score += -1
        elif "" in self.tmpline :
            self.data_error_empty += 1
            if self.data_error_empty <= self.error_print_cnt :
                self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " has empty column ==> " + str(self.tmpline).decode('string_escape') + "\n"
                self.error_msg_mongo["format"]["empty"].append(self.tmpline)
            self.score += -1
        else :
            for i in self.exclude_char :
                strline = str(self.tmpline).decode('string_escape')
                if i in strline :
                    self.data_error_special_char += 1
                    if self.data_error_special_char <= self.error_print_cnt :
                        self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " has spacial char [" + i + "] ==> " + str(self.tmpline).decode('string_escape') + "\n"
                        self.error_msg_mongo["format"]["specialchar"].append(self.tmpline)
                    self.score += -1
                    break

    def datetimespec(self, dateidx) :
        if self.tmpline[dateidx].find("T") < 0 :
            self.date_error_t += 1
            if self.date_error_t <= self.error_print_cnt :
                self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " wrong datetime format ==> " + str(self.tmpline).decode('string_escape') + "\n"
                self.error_msg_mongo["format"]["date"].append(self.tmpline)
            self.score += -1
        elif len(self.tmpline[dateidx]) != 19 :
            self.date_error_len += 1
            if self.date_error_len <= self.error_print_cnt :
                self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " wrong datetime length ==> " + str(self.tmpline).decode('string_escape') + "\n"
                self.error_msg_mongo["format"]["date"].append(self.tmpline)
            self.score += -1
        else :
            # only calculate correct date format data 
            if self.checkdealdetail :
                if self.now_dir == "header" :
                    if self.tmpline[2] != "null" :
                        member = "-999"
                        self.customer_cnt += 1
                    else :
                        member = self.tmpline[2]
                        self.noncustomer_cnt += 1
                    key = self.tmpline[dateidx][0:10]
                    self.data_set_date.add((key, member))
                elif self.now_dir == "transaction" :
                    key = self.tmpline[dateidx][0:10]
                    self.data_set_date.add((key,""))    

    def overalldataname(self):
        filename, filetype = self.tmpfile.split(".")
        split_idx = filename[4:].find("-")
        if split_idx < 0 :
            self.tmpfile = filename
        else :
            self.tmpfile = filename[:(split_idx+4)]

    def ftpdataformat(self, filepath, filelist) :
        for i in filelist :
            self.tmpfile = i
            self.overalldataname()
            self.now_filename = filepath + "/" + i
            self.setfiledefault()
 
            if i.find(".zip") > 0 :
                z = zipfile.ZipFile(self.now_filename, "r")
                f = z.open(z.namelist()[0], "r")            
            else :    
                f = open(self.now_filename, "rb")
           
            for line in f :
                self.tmpline = line.strip().replace('"','').split(",")
                colcnt = len(self.tmpline)
               
                if self.now_dir == self.ftp_src_dir[4] : #member
                    if colcnt != 14 :
                        self.data_error_cnt += 1
                        if self.data_error_cnt <= self.error_print_cnt : 
                            self.error_msg += "[data - member] - " + self.now_filename + " wrong schema != 14 ==> " + str(self.tmpline).decode('string_escape') + "\n"
                            self.error_msg_mongo["format"]["schema"].append(self.tmpline)
                        self.score += -1
                    elif self.tmpline[0] == "" :
                        self.data_error_empty += 1
                        if self.data_error_empty <= self.error_print_cnt :
                            self.error_msg += "[data - member] - " + self.now_filename + " empty member id(1) ==> " + str(self.tmpline).decode('string_escape') + "\n"
                            self.error_msg_mongo["format"]["empty"].append(self.tmpline)
                        self.score += -1
                    elif self.tmpline[0].find("-") > -1 :
                        self.data_error_special_char += 1
                        if self.data_error_special_char <= self.error_print_cnt :
                            self.error_msg += "[data - member] - " + self.now_filename + " couldn't use ['-'] ==> " + str(self.tmpline).decode('string_escape') + "\n"
                            self.error_msg_mongo["format"]["specialchar"].append(self.tmpline)
                        self.score += -1 
                 
                elif self.now_dir == self.ftp_src_dir[3] : #store
                    self.dataspec(5, colcnt)
                
                elif self.now_dir == self.ftp_src_dir[2] : #item
                    self.dataspec(5, colcnt)
                
                elif self.now_dir == self.ftp_src_dir[0] : #header
                    self.dataspec(4, colcnt)
                    if self.tmpline[2].find("-") > -1 :
                        self.data_error_special_char += 1
                        if self.data_error_special_char <= self.error_print_cnt :
                            self.error_msg += "[data - header] - " + self.now_filename + " couldn't use ['-'] ==> " + str(self.tmpline).decode('string_escape') + "\n"
                            self.error_msg_mongo["format"]["specialchar"].append(self.tmpline)
                        self.score += -1

                    if self.checkdealdate :
                        self.datetimespec(1)

                elif self.now_dir == self.ftp_src_dir[1] : #transaction
                    if colcnt != 7 :
                        self.data_error_cnt += 1 
                        if self.data_error_cnt <= self.error_print_cnt :
                            self.error_msg += "[data - transaction] - " + self.now_filename + " wrong schema != 7 ==> " + str(self.tmpline).decode('string_escape') + "\n"
                            self.error_msg_mongo["format"]["schema"].append(self.tmpline) 
                        self.score += -1
                    elif "" in [self.tmpline[1], self.tmpline[2], self.tmpline[5], self.tmpline[6]] :
                        self.data_error_empty += 1
                        if self.data_error_empty <= self.error_print_cnt :
                            self.error_msg += "[data - transaction] - " + self.now_filename + " trx_id(2), item_id(3), money(6), date(7) shouldn't be empty ==> " + str(self.tmpline).decode('string_escape') + "\n"
                            self.error_msg_mongo["format"]["empty"].append(self.tmpline)
                        self.score += -1
                    else :
                        if self.checkdealdate :
                            self.datetimespec(6)

            if self.checkdealdetail :
                if self.now_dir == self.ftp_src_dir[0] or self.now_dir == self.ftp_src_dir[1]:
                    nameidx = 0
                    if self.datatype == "historical" :
                        nameidx = 4 

                    filename = i[nameidx:-4].split("-")
                    filedate = dt.datetime.strptime(filename[0][-8:], '%Y%m%d').strftime('%Y-%m-%d')
                    self.dealdetail(filedate)
                    
            self.error_msg_dir_mongo["data"].append(self.error_msg_mongo) 
            self.dir_score += self.score
            if self.score < 0 :
                self.error_msg += "-------------------------------------------- [" + self.now_filename + " ] ==> File Score " + str(self.score) + "------------------------------------------------\n\n"

    def ftpdatamark(self, data_list, data_mark_list, replacestr, namesep, mark, filepath) :
        for i in data_list :
            line = i.split(".")
            split_idx = line[0].replace(replacestr,"").find(namesep)
            src_file_name = ""

            #skip historical mark "MIX-", when substring should add 
            if self.datatype == "historical" :
                split_idx = (split_idx + 4) 

            # MIX-JTWR_orderdetail_20150427-1.zip   MIX-JTWR_orderdetail_20150402.zip 
            if split_idx > 0 :
                src_file_name = line[0][0:split_idx]
            else :
                src_file_name = line[0]

            if (src_file_name + mark) not in data_mark_list :
                self.error_msg += "[ftp - " + self.now_dir + "] - " + filepath + ": " + line[0] + " "  + self.datatype + " data no mark [" + mark + "] file \n"
                self.error_msg_dir_mongo["overall"]["mark"][self.datatype].append(line[0] + " "  + self.datatype + " data no mark [" + mark + "] file ")
                self.dir_score += -1

    def ftpfilerule(self, ftp_src_path) :
        """
        check dir status, data detail error plus score, other for dir_score
        """ 
        if not os.path.exists(ftp_src_path) or os.stat(ftp_src_path).st_size == 0 :
            self.error_msg += "[ftp" + " - " + self.now_dir+ "] - " + ftp_src_path + " is not exist \n"
            self.error_msg_dir_mongo["overall"]["path"]["dir"] = self.now_dir + " is not exist "
            self.dir_score += -1
        else :
            ftp_src_file = os.listdir(ftp_src_path)
            if len(ftp_src_file) == 0 :
                self.error_msg += "[ftp" + " - " + self.now_dir + "] - " + ftp_src_path + " no data \n"
                self.error_msg_dir_mongo["overall"]["file"] = " no data "
                self.dir_score += -1
            else :
                if self.checkInc :
                    src_Inc = filter(lambda x: "MIX-" not in x and ".done" not in x, ftp_src_file)
                    if len(src_Inc) > 0 :
                        self.datatype = self.ftp_mark_file_type.keys()[0]
                        if self.checkmark :
                            src_Inc_Mark = filter(lambda x: ".done" in x, ftp_src_file)
                            self.ftpdatamark(src_Inc, src_Inc_Mark, "", "-", self.ftp_mark_file_type[self.datatype], ftp_src_path)
                        if self.checkformat :
                            self.ftpdataformat(ftp_src_path, src_Inc)
                    else :
                        self.error_msg += "[ftp" + " - " + self.now_dir + "] - " + ftp_src_path + " no incremental data \n"
                        self.error_msg_dir_mongo["overall"]["mark"]["incremental"].append(" no incremental data ")
                        self.dir_score += -1

                if self.checkHis :
                    src_His = filter(lambda x: "MIX-" in x and ".full" not in x, ftp_src_file)
                    if len(src_His) > 0 :
                        self.datatype = self.ftp_mark_file_type.keys()[1]
                        if self.checkmark : 
                            src_His_Mark = filter(lambda x: ".full" in x, ftp_src_file)
                            self.ftpdatamark(src_His, src_His_Mark, "MIX-", "-", self.ftp_mark_file_type[self.datatype], ftp_src_path) 
                        if self.checkformat :
                            self.ftpdataformat(ftp_src_path, src_His)
                    else :
                        self.error_msg += "[ftp" + " - " + self.now_dir + "] - " + ftp_src_path + " no historical data \n"
                        self.error_msg_dir_mongo["overall"]["mark"]["historical"].append(" no historical data ")
                        self.dir_score += -1
     
    def hadoopresult(self, hadoop_path):
        for i in self.hadoop_result_dir :
            file_path = hadoop_path + "/" + i
            cmd = "hadoop fs -du {} ".format(file_path)
            status, output = commands.getstatusoutput(cmd)
        
            if status != 0 :
                self.error_msg += "[hadoop] - " + file_path + " is not exist \n"
            else :
                line = output.split("\n")
                for i in line :
                    size = i[0:i.index("/")].replace(" ","")
                    path = i[i.index("/"):]
           
                    if size == "0" :
                        self.error_msg += "[hadoop] - " + path + " is empty \n"
        
def writefile(filename, msg) :
    file = open(filename, "a")
    file.write(msg)
    file.close()

def getinputpar(parameter_list) :
    parameter_dict = {"checkdir":"-999" ,"checkftp":False, "checkhadoop":False, "shop_id":"-999", "checkHis":False, "checkInc":False, "checkmark":False, "checkformat":False, "checkdealdate":False, "checkdealdetail":False, "error_print_cnt":2 }
    lastinputparidx = len(parameter_list) - 1
    for idx,val in enumerate(parameter_list) :
        if idx == 0 or val.find("--") < 0 :
            continue
        else :
            key = val.replace("--","")

            if (idx + 1) > lastinputparidx or parameter_list[(idx + 1)].find("--") > -1 :
                if key == "error_print_cnt" :
                    parameter_dict[key] = 1
                elif key == "checkdir" or key == "shop_id" :
                    continue
                else :
                    parameter_dict[key] = True
            else :
                parameter_dict[key] = parameter_list[(idx + 1)]
    return parameter_dict

if __name__ == "__main__" :
    """
    #Job Name:      DataCheck
    #Objectives:    check ftp uploaded data or hadoop final result data 
    #Author:    Cindy Tseng
    #Created Date:  2015.05.18
    #Source:        [ftp] :     /data/diy-data/(shop_id)/upload
                    [hadoop] :  /user/athena/(shop_id)
    #Destination:   file path
    #Usage:         
                    parameter description:
                        0.  --checkdir : check ftp single dir, if not set it will check all dirs
                        1.  --shop_id
                        2.  --checkftp  / --checkhadoop : check ftp or hadoop data, can use both
                        3.  --checkInc  / --checkHis    : check ftp incremental or historical data, can use both 
                        4.  --checkmark   : check ftp data mark file
                        5.  --checkformat : check ftp data format, use with (5.1~5.3)
                        5.1 --checkdealdate   : check ftp data, the transaction date in heder or transaction file
                        5.2 --checkdealdetail : cheche ftp data, the transaction detail (lose days, date range, file date match data date, customer data percentage.....) 
                        5.3 --error_print_cnt : print ftp error data count 

                        [check-ftp]       ==> ./datacheck.py --shop_id jtwk --checkftp --checkInc --checkHis --checkmark --checkformat --checkdealdate --checkdealdetail --error_print_cnt 10
                        [check-hadoop]    ==> ./datacheck.py --shop_id ablejeans --checkhadoop 

    #mongo:         only for ftp 
                    1. all dir     ==> { "Src" : shopid, "Status" :dir, "Dest" : whole path }
                    2. every file  ==> { "Src" : shopid, "Status" : {errormsg}, "Dest" : whole path}
    """ 

    parameter_dict = getinputpar(sys.argv)
    checkftp, checkhadoop =  bool(parameter_dict["checkftp"]), bool(parameter_dict["checkhadoop"])
    shop_id, error_print_cnt = parameter_dict["shop_id"], int(parameter_dict["error_print_cnt"])
    checkHis, checkInc  = bool(parameter_dict["checkHis"]), (parameter_dict["checkInc"])
    checkmark = bool(parameter_dict["checkmark"])
    checkformat, checkdealdate, checkdealdetail = bool(parameter_dict["checkformat"]), bool(parameter_dict["checkdealdate"]), bool(parameter_dict["checkdealdetail"])

    ftp_src_dir = []   
    dc = DataCheck(shop_id, checkftp, checkhadoop, checkmark, checkHis, checkInc, checkformat, checkdealdate, checkdealdetail, error_print_cnt)      
    if parameter_dict["checkdir"] == "-999" :
        ftp_src_dir = dc.ftp_src_dir
    else :
        ftp_src_dir.append(parameter_dict["checkdir"])

    if not checkftp and not checkhadoop :
        print "plz choose what u want to check ftp data or hadoop data, usage as following : \n [ ./check_new.py --shop_id (--checkftp/--checkhadoop) (--checkInc/--checkHis) --checkmark --checkformat --checkdealdate --checkdealdetail  --error_print_cnt 10]"
    if checkftp :
        for i in ftp_src_dir :
            dc.error_msg = ""
            dc.dir_score, dc.now_dir = 0, i
            dc.setdirdefault()
            ftp_src_path = dc.ftp_src_path + "/" + dc.now_dir

            dc.start_time = time.mktime( datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S").timetuple() )
            dc.ftpfilerule(ftp_src_path)
            dc.end_time = time.mktime( datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S").timetuple() )

            dc.count_failed = -(dc.dir_score)
            dc.src = ftp_src_path.replace("/","^")
            dc.status = dc.now_dir
            dc.url = "{}/{}/{}/{}/{}/{}/{}/{}/{}/".format(MIGO_DJANGO_MONITOR_API, dc.task_name, dc.status, dc.src, dc.dest, dc.count_success, dc.count_failed, dc.start_time, dc.end_time)

            if dc.checkHis and dc.checkInc :
                dc.final_msg += "[final" + " - " + dc.now_dir + "] - " + ftp_src_path + " total score for " + str(dc.dir_score) + "\n"
            elif dc.checkHis :
                dc.final_msg += "[final" + " - " + dc.now_dir + "] - " + ftp_src_path + " total score for [ historical data ] " + str(dc.dir_score) + "\n"
            else :
                dc.final_msg += "[final" + " - " + dc.now_dir + "] - " + ftp_src_path + " total score for [ incremental data ] " + str(dc.dir_score) + "\n"

            writefile(("/tmp/cindy/" + dc.shop_id + ".txt"), dc.error_msg)
            insertjson = {
            "TaskID" : dc.task_name,
            "Status" : dc.error_msg_dir_mongo,
            "StartTime" : dc.start_time, "EndTime" : dc.end_time,
            "CountSuccess" : dc.count_success,
            "CountFailed" : dc.count_failed,
            "Src" : dc.src, "Dest" : "no",
            }
            #dc.savemongo(insertjson)
            
            #overall deal conclusion ==> date range, losedays,customer deal percentage
            for val in dc.overalldata.keys():
                losedaystr = ""
                losedays = len(dc.overalldata[val]["losedays"])
                if losedays > 0 :
                    losedaystr = " losdays for " + str(len(dc.overalldata[val]["losedays"])) + " days => " + str(list(dc.overalldata[val]["losedays"]))
                print "[final" + " - " + dc.now_dir + "] - " + val + " date between [ " + min(dc.overalldata[val]["daterange"]) + " ~ " + max(dc.overalldata[val]["daterange"]) + " ] " + losedaystr
            if dc.now_dir == "header" :
                for val in dc.customer_deal_type.keys():
                    print "[final" + " - " + dc.now_dir + "] - " + val + " " + str(round((float(dc.customer_deal_type[val][0]) / float(dc.customer_deal_type[val][0] + dc.customer_deal_type[val][1])) * 100 ,2 )) + " % " + " customer data "

        print dc.final_msg   

    if checkhadoop :
        dc.error_msg = ""
        one_time_result = dc.hadoop_path + dc.client
        dc.hadoopresult(one_time_result)
        print dc.error_msg

