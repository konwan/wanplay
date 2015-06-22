#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os, getpass
sys.path.append("/data/migo/athena/lib")
from athena_variable import *

import time, datetime as dt
#from time import gmtime, strftime
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

        self.score, self.dir_score = 0, 0       
        self.error_msg, self.final_msg = "", ""
        self.error_msg_mongo = {"path":{ "dir":"", "file":"" }, 
                                "mark":{ "historical":"", "incremental":""}, 
                                "format":{"schema":[], "empty":[], "specialchar":[], "date":[], "others":[] }, 
                                "detail":{"losedays":"", "filedatenotmatch":""}
                               }

        # data upload source
        self.ftp_src_path = "/data/diy-data/" + shop_id + "/upload"
        #self.ftp_src_path = "/home/cindy/diy/athena/modules/check/" + shop_id
        #self.ftp_src_dir = ["header","transaction","1","2","3"]
        self.ftp_src_dir = ["header","transaction","item","store","member"]
        self.ftp_src_file_type = [".csv", ".zip", ".txt"]
        self.ftp_mark_file_type = {"historical":".full", "incremental":".done"}
        self.datatype, self.now_dir, self.now_filename = "", "", ""

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
        #hadoop_result_dir = ["activeness_week"]
        self.exclude_char = ["!","@","#","$","%","^","&","*","~","@","?"]
        self.setdefault()

        self.task_name = self.__class__.__name__ 
        self.status, self.url, self.src, self.dest = "", "", "", ""
        self.start_time, self.end_time = "", ""
        self.count_success, self.count_failed = 0, 0
        
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


    def test(self) : 
        print  "shop, checkmark, checkHis, checkInc, checkformat, checkdealdate, checkdealdetail, error_print_cnt ==> " + self.shop_id, str(self.checkmark), str(self.checkHis), str(self.checkInc), str(self.checkformat), str(self.checkdealdate), str(self.checkdealdetail), str(self.error_print_cnt)

    def setdefault(self) :
        self.score = 0
        self.date_error_t, self.date_error_len, self.data_error_cnt, self.data_error_empty, self.data_error_special_char = 0, 0, 0, 0, 0
        self.data_set_date = set()
        self.data_dict_date = {}
        self.dealfirstday, self.deallastday = "", ""
        self.status, self.url, self.src, self.dest = "", "", "", ""
        self.start_time, self.end_time = "", ""
        self.count_success, self.count_failed = 0, 0

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
                self.dir_score += -1

       
    def dataspec(self, line, standcolcnt, colcnt) :
        if standcolcnt != colcnt :
            self.data_error_cnt += 1
            if self.data_error_cnt <= self.error_print_cnt :
                self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " wrong schema != " + str(colcnt) + " ==> " + str(line).decode('string_escape') + "\n"
            self.score += -1
        elif "" in line :
            self.data_error_empty += 1
            if self.data_error_empty <= self.error_print_cnt :
                self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " has empty column ==> " + str(line).decode('string_escape') + "\n"
            self.score += -1
        else :
            for i in self.exclude_char :
                strline = str(line).decode('string_escape')
                if i in strline :
                    self.data_error_special_char += 1
                    if self.data_error_special_char <= self.error_print_cnt :
                        self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " has spacial char [" + i + "] ==> " + str(line).decode('string_escape') + "\n"
                    self.score += -1
                    break

    def datetimespec(self, line, dateidx) :
        member = ""
        if line[dateidx].find("T") < 0 :
            self.date_error_t += 1
            if self.date_error_t <= self.error_print_cnt :
                self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " wrong datetime format ==> " + str(line).decode('string_escape') + "\n"
            self.score += -1
        elif len(line[dateidx]) != 19 :
            self.date_error_len += 1
            if self.date_error_len <= self.error_print_cnt :
                self.error_msg += "[data - " + self.now_dir + "] - " + self.now_filename + " wrong datetime length ==> " + str(line).decode('string_escape') + "\n"
            self.score += -1
        else :
            if self.checkdealdetail :
                if self.now_dir == "header" :
                    if line[2] != "null" :
                        member = "-999"
                    else :
                        member = line[2]
                    key = line[dateidx][0:10]
                    self.data_set_date.add((line[1][0:10], member))

                elif self.now_dir == "transaction" :
                    key = line[dateidx][0:10]
                    self.data_set_date.add((line[6][0:10],""))

    def dealdetail(self, filedate) :
        for i in self.data_set_date :
            if i[0] not in self.data_dict_date.keys() :
                self.data_dict_date[i[0]] = []
            self.data_dict_date[i[0]].append(i[1])

        if self.now_dir == "header" :
            for i in sorted(self.data_dict_date.keys()) :
                if len(self.data_dict_date[i]) < 2 and "-999" not in self.data_dict_date[i] :
                    self.error_msg += "[data" + " - " + self.now_dir + "] - " + self.now_filename + " [" + i + "] only have noncustomer data \n"
                    self.score += -1

        if filedate not in self.data_dict_date.keys() :
            self.error_msg += "[data" + " - " + self.now_dir + "] - " + self.now_filename + " no [" + filedate + "] data in the file \n"
            self.score += -1

        self.dealfirstday, self.deallastday = min(self.data_dict_date.keys()), max(self.data_dict_date.keys())
        if self.datatype == "incremental" :
            if len(self.data_dict_date.keys()) > 1 :
                self.error_msg += "[data" + " - " + self.now_dir + "] - " + self.now_filename + " not only [" + filedate + "] data \n"
                self.score += -1
            if self.dealfirstday != self.deallastday :
                self.error_msg += "[final" + " - " + self.now_dir + "] - " + self.now_filename + " deal date is between [ " + self.dealfirstday + " ~ " + self.deallastday + " ]\n"
        else :            
            losedays = self.dealdatelose()
            losedayscnt = len(losedays)
            if losedayscnt != 0 :
                self.error_msg += "[final" + " - " + self.now_dir + "] - " + self.now_filename + " lose " +str(losedayscnt) + " days data ====> \n" + str(losedays) + "\n"
                self.score += -1     

            self.error_msg += "[final" + " - " + self.now_dir + "] - " + self.now_filename + " deal date is between [ " + self.dealfirstday + " ~ " + self.deallastday + " ]\n"

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

    def ftpdataformat(self, filepath, filelist) :
      
        for i in filelist :
            self.setdefault()
            self.now_filename = filepath + "/" + i

            if i.find(".zip") > 0 :
                z = zipfile.ZipFile(self.now_filename, "r")
                f = z.open(z.namelist()[0], "r")            
            else :    
                f = open(self.now_filename, "rb")
           
            for line in f :
                line = line.strip().replace('"','').split(",")
                colcnt = len(line)
               
                if self.now_dir == self.ftp_src_dir[4] : #member
                    if colcnt != 14 :
                        self.error_msg += "[data - member] - " + self.now_filename + " wrong schema != 14 ==> " + str(line).decode('string_escape') + "\n"
                        self.score += -1
                    elif line[0] == "" :
                        self.error_msg += "[data - member] - " + self.now_filename + " empty member id(1) ==> " + str(line).decode('string_escape') + "\n"
                        self.score += -1                 
                 
                elif self.now_dir == self.ftp_src_dir[3] : #store
                    self.dataspec(line, 5, colcnt)
                
                elif self.now_dir == self.ftp_src_dir[2] : #item
                    self.dataspec(line, 5, colcnt)
                
                elif self.now_dir == self.ftp_src_dir[0] : #header
                    self.dataspec(line, 4, colcnt)
                    if self.checkdealdate :
                        self.datetimespec(line, 1)

                elif self.now_dir == self.ftp_src_dir[1] : #transaction
                    if colcnt != 7 :
                        self.error_msg += "[data - transaction] - " + self.now_filename + " wrong schema != 7 ==> " + str(line).decode('string_escape') + "\n"
                        self.score += -1
                    elif "" in [line[1], line[2], line[5], line[6]] :
                        self.error_msg += "[data - transaction] - " + self.now_filename + " trx_id(2), item_id(3), money(6), date(7) shouldn't be empty ==> " + str(line).decode('string_escape') + "\n"
                        self.score += -1
                    else :
                        if self.checkdealdate :
                            self.datetimespec(line, 6)
              
            if self.checkdealdetail :
                if self.now_dir == self.ftp_src_dir[0] or self.now_dir == self.ftp_src_dir[1]:
                    nameidx = 0
                    if self.datatype == "historical" :
                        nameidx = 4 

                    filename = i[nameidx:-4].split("-")
                    filedate = dt.datetime.strptime(filename[0][-8:], '%Y%m%d').strftime('%Y-%m-%d')
                    self.dealdetail(filedate)
            
            self.dir_score += self.score
            if self.score < 0 :
                self.error_msg += "-------------------------------------------- [" + self.now_filename + " ] ==> Final Score " + str(self.score) + "------------------------------------------------\n"

    def ftpfilerule(self, ftp_src_path) : 
        #ftp_src_path = self.ftp_src_path + "/" + self.now_dir
        if not os.path.exists(ftp_src_path) or os.stat(ftp_src_path).st_size == 0 :
            self.error_msg += "[ftp" + " - " + self.now_dir+ "] - " + ftp_src_path + " is not exist \n"
            self.dir_score += -1
        else :
            ftp_src_file = os.listdir(ftp_src_path)
            if len(ftp_src_file) == 0 :
                self.error_msg += "[ftp" + " - " + self.now_dir + "] - " + ftp_src_path + " has no data \n"
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
                        self.error_msg += "[ftp" + " - " + self.now_dir + "] - " + ftp_src_path + " can't find incremental data \n"
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
                        self.error_msg += "[ftp" + " - " + self.now_dir + "] - " + ftp_src_path + " can't find historical data \n"
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
    #Author:	Cindy Tseng
    #Created Date:  2015.05.18
    #Source:        [ftp] :     /data/diy-data/(shop_id)/upload
                    [hadoop] :  /user/athena/(shop_id)
    #Destination:   file path
    #Usage:         
                    parameter description:
                        0.  --checkdir : check ftp single dir, if not set it will check all dirs
                        1.  --shop_id
                        2.  --checkftp / --checkhadoop : check ftp or hadoop data, can use both
                        3.  --checkInc / --checkHis    : check ftp incremental or historical data, can use both 
                        4.  --checkmark   : check ftp data mark file
                        5.  --checkformat : check ftp data format, use with (5.1~5.3)
                        5.1 --checkdealdate   : check ftp data, the transaction date in heder or transaction file
                        5.2 --checkdealdetail : cheche ftp data, the transaction detail (lose days, date range, file date match data date .....) 
                        5.3 --error_print_cnt : print ftp error data count 

                        [check-hadoop] ==> ./check_new.py --shop_id jtwk --checkftp --checkInc --checkHis --checkmark --checkformat --checkdealdate --checkdealdetail --error_print_cnt 10
                        [check-ftp]    ==> ./check_new.py --shop_id ablejeans --checkhadoop 

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
            dc.setdefault()
            dc.start_time = time.mktime( datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S").timetuple() )
            dc.error_msg = ""
            dc.dir_score = 0
            dc.now_dir = i
            ftp_src_path = dc.ftp_src_path + "/" + dc.now_dir
            dc.ftpfilerule(ftp_src_path)
            dc.end_time = time.mktime( datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S").timetuple() )

            dc.count_failed = -(dc.dir_score)
            dc.dest = ftp_src_path.replace("/","^")
            dc.status = dc.now_dir
            dc.src = dc.shop_id
            dc.url = "{}/{}/{}/{}/{}/{}/{}/{}/{}/".format(MIGO_DJANGO_MONITOR_API, dc.task_name, dc.status, dc.src, dc.dest, dc.count_success, dc.count_failed, dc.start_time, dc.end_time)

            if dc.checkHis and dc.checkInc :
                dc.final_msg += "[final" + " - " + dc.now_dir + "] - " + ftp_src_path + " total score for " + str(dc.dir_score) + "\n"
            elif dc.checkHis :
                dc.final_msg += "[final" + " - " + dc.now_dir + "] - " + ftp_src_path + " total score for [ historical data ] " + str(dc.dir_score) + "\n"
            else :
                dc.final_msg += "[final" + " - " + dc.now_dir + "] - " + ftp_src_path + " total score for [ incremental data ] " + str(dc.dir_score) + "\n"

            writefile((dc.ftp_src_path + "/datalog.txt"), dc.error_msg)
            print dc.final_msg

    if checkhadoop :
        dc.error_msg = ""
        one_time_result = dc.hadoop_path + dc.client
        dc.hadoopresult(one_time_result)
        print dc.error_msg


