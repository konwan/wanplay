#!/usr/bin/env python

import sys
sys.path.append("/data/migo/athena/lib")

from athena_variable import *
from athena_luigi import *

import re, mathi
from datetime import datetime

import luigi, luigi.hadoop, luigi.hdfs

#class Test(luigi.hadoop.JobTask):
class Test(MigoLuigiHdfs):

    def start(self):
	pass

    def extra_files(self):
	return []

    def remove_files(self):
	return [self.dest]

    def requires(self):
        if self.use_hadoop:
            return CleanerHDFS(self.src)
        else:
            return CleanerLocal(self.src)


    def output(self):
        if self.use_hadoop:
            return luigi.hdfs.HdfsTarget(self.dest)
        else:
            return luigi.LocalTarget(self.dest)


    #def reducer(self, key, values):
    #    pass


    def mapper(self, line):
        shop_id, member_id, ordate, money = line.strip().split(MIGO_SEPARATOR_LEVEL1)
        yield "{}_{}~{}".format(shop_id, member_id, money),


##############################  main   #######################################
if __name__=='__main__':
    luigi.run()
