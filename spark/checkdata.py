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
from operator import itemgetter

if __name__ == "__main__" :
    now = datetime.date.today()


    files = ["hdfs://10.10.21.25:8020/user/migo/starterDIY/shirble/member/done/*", "hdfs://10.10.21.25:8020/user/migo/starterDIY/meishilin/member/done/*", "hdfs://10.10.21.25:8020/user/migo/starterDIY/huaguan/member/done/*", "hdfs://10.10.21.25:8020/user/migo/starterDIY/sunshine/member/done/*"]
    sb = "hdfs://{hdfsmaster}:8020/user/migo/starterDIY/shirble/member/done/*, hdfs://{hdfsmaster}:8020/user/migo/starterDIY/meishilin/member/done/*".format(hdfsmaster=MIGO_HDFS_MASTER)
    #ss = "hdfs://{hdfsmaster}:8020/user/migo/starterDIY/{shop}/member/done/*".format(hdfsmaster=MIGO_HDFS_MASTER, shop="sunshine")
    #hg = "hdfs://{hdfsmaster}:8020/user/migo/starterDIY/{shop}/member/done/*".format(hdfsmaster=MIGO_HDFS_MASTER, shop="huaguan")
    #ms = "hdfs://{hdfsmaster}:8020/user/migo/starterDIY/{shop}/member/done/*".format(hdfsmaster=MIGO_HDFS_MASTER, shop="meishilin")

    cf = SparkConf().setAppName("[SQL] check data {}".format(datetime.datetime.now()))
    sc = SparkContext(conf = cf)

    raw_sb = sc.textFile(','.join(files))
    #raw_ss = sc.textFile(ss)
    #raw_hg = sc.textFile(hg)
    #raw_ms = sc.textFile(ms)

    data_index = [0,1,4,6,8,9,10,11]


    rsb = raw_sb.map(lambda line: [ x.replace("\"","") for x in list( itemgetter(*data_index)( line.split(",") ) )] )\
                .map(lambda p: Row(shop=p[0], mid=p[1], mob=p[2], id=p[3], gender=p[4], bir=p[5], pro=p[6], city=p[7]))


    sqlContext = SQLContext(sc)

    schemasb = sqlContext.createDataFrame(rsb)
    schemasb.registerTempTable("sb")

    schemasb.show()
    #schemasb.printSchema()
    #schemasb.groupBy("shop")fgdiuhr43urjgerergihio;.count().show()
    rddsql = " SELECT shop, count(*) as cnt FROM sb where mob='' group by shop " + " union " + "SELECT shop, count(*) as cnt FROM sb where mob!='' group by shop "

    test = " select shop, mob, id, gen, bir, pro, city, count(*) as cnt from  (select shop , (case when mob!='' then 'y' else 'n' end) as mob, (case when id!='' then 'y' else 'n' end) as id, (case when gender!='' then 'y' else 'n' end) as gen, (case when bir!='' then 'y' else 'n' end) as bir, (case when pro!='' then 'y' else 'n' end) as pro, (case when city!='' then 'y' else 'n' end) as city from sb ) as a group by shop, mob, id, gen, bir, pro, city order by shop"


    sbresult = sqlContext.sql(test).show()

    #sbsql = sqlContext.sql("select sex, age, count(*) as cnt from mt group by sex, age").map(lambda p: "({}{sep}{},{})".format(p.sex, p.age, p.cnt, sep=MIGO_TMP_SEPARATOR))
    #print  mebsql.collect()



    sc.stop()
