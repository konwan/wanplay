#!/usr/bin/env python

import sys
sys.path.append("/data/migo/athena/lib")

from athena_variable import *
from athena_luigi import *

import re, math
from datetime import datetime

import luigi, luigi.hadoop, luigi.hdfs

#class Test(luigi.hadoop.JobTask):
class Test(luigi.hadoop.JobTask):
    use_hadoop = luigi.BooleanParameter()
    is_delete = luigi.BooleanParameter()
    source = luigi.Parameter(default="data_prepare")
    destination = luigi.Parameter(default="order_sum")

    def initialized(self):
        hdfsClient = luigi.hdfs.HdfsClient()
        if self.is_delete and hdfsClient.exists(self.destination):
            hdfsClient.remove(self.destination)
        return super(Test, self).initialized()

    def requires(self):
        if self.use_hadoop:
            return CleanerHDFS(self.source)
        else:
            return CleanerLocal(self.source)

    def output(self):
        if self.use_hadoop:
            return luigi.hdfs.HdfsTarget(self.destination)
        else:
            return luigi.LocalTarget(self.destination)

    #def reducer(self, key, values):
    #    pass


    def mapper(self, line):
        shop_id, member_id, ordate, money = line.strip().split(MIGO_SEPARATOR_LEVEL1)
        #shop_id, money = line.split(MIGO_SEPARATOR_LEVEL1)
        #shop_id, member_id, ordate, money = line.split("\t")
        yield "{}_{}~{}".format(shop_id, member_id, money),
        #yield line.split(MIGO_SEPARATOR_LEVEL1),
	#yield line,

##############################  main   #######################################
if __name__=='__main__':
    luigi.run()
