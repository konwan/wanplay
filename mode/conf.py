#!/usr/bin/env python
#coding=UTF-8

import os
import sys
sys.path.append("/data/migo/athena/lib")
from athena_variable import *

import ConfigParser


"""
Job Task:       
Objective:      read conf
Author:         Cindy Tseng
Created Date:   2016.09.20
"""


class ApiConf:
    #conf_file = "/home/cindy/athena/mode/conf.ini"            
    conf_file = "/data/migo/athena/mode/conf.ini"

    def __init__(self, mode, hdfs_mode):
        self.conf = ConfigParser.ConfigParser()
        self.conf.read(self.conf_file)
        self.mode = mode
        self.hdfs_mode = hdfs_mode
        self.start()
        if mode != "" or hdfs_mode != "":
            self.setConf()

    def start(self):
        if self.mode == "" :
            self.mode = self.conf.get("mode", "get_data_mode")
        elif self.mode == "hdfs" :
            if self.hdfs_mode == "":
                self.hdfs_mode = self.conf.get("hdfs", "use_hdfs_mode")

    def setConf(self):
        cf = open(self.conf_file,'w')
        self.conf.set("mode", "get_data_mode", self.mode)
        self.conf.set("hdfs", "use_hdfs_mode", self.hdfs_mode)
        self.conf.write(cf)
        cf.close()

    def getPath(self):
        if self.mode == "local":
            meball = self.conf.get("local", "file_path_pre")
        elif self.mode == "hdfs":
            if self.hdfs_mode == "cluster":
                usingport = self.conf.get("hdfs", "cluster_port")
            else :
                usingport = self.conf.get("hdfs", "single_port")
            meball = self.conf.get("hdfs", "hdfs_path_pre").format(hdfsmaster=MIGO_HDFS_MASTER, port = usingport)
        else :
            meball = self.conf.get("other", "other_path_pre")
        return meball

# test conf.py 
if __name__ == "__main__":
    mode = sys.argv[1]
    hdfs_mode = sys.argv[2]

    ac = ApiConf(mode, hdfs_mode)
    path = ac.getPath()


    print path
