#!/usr/bin/env python

import sys
sys.path.append("/data/migo/athena/lib")

from athena_variable import *
from athena_luigi import *

import re, datetime

import luigi, luigi.hdfs, luigi.hadoop
from luigi import BooleanParameter, Parameter, IntParameter, Task
from luigi.hdfs import HdfsTarget

class ParetoAnalysisMean(luigi.hadoop.JobTask):
    use_hadoop = BooleanParameter()
    key_idx = IntParameter()
    value_idx = IntParameter()
    source = Parameter()
    destination = Parameter()

    def output(self):
        if self.use_hadoop:
            return HdfsTarget(self.destination)
        else:
            return LocalTarget(self.destination)

    def requires(self):
        if self.use_hadoop:
            return CleanerHDFS(self.source)
        else:
            return CleanerLocal(self.source)

    def mapper(self, line):
        infos = line.split(MIGO_SEPARATOR_LEVEL1)

        yield infos[self.key_idx-1], (float(infos[self.value_idx-1]), 1)

    def sum(self, values):
        num_sum, num = 0, 0
        for value in values:
            num_sum += value[0]
            num += value[1]

        return num_sum, num

    def combiner(self, key, values):
        yield key, self.sum(values)

    def reducer(self, key, values):
        all, num = self.sum(values)

        yield key, "!%f" %(all/num)

class ParetoAnalysisHighMean(luigi.hadoop.JobTask):
    use_hadoop = BooleanParameter()
    key_idx = IntParameter()
    value_idx = IntParameter()
    source = Parameter()
    destination = Parameter()

    def jobconfs(self):
        self.separator = "|"

        jcs = super(luigi.hadoop.JobTask, self).jobconfs()

        jcs.append("mapreduce.map.output.key.field.separator=%s" %self.separator)
        jcs.append("mapreduce.partition.keypartitioner.options=-k1,1")

        return jcs

    def output(self):
        if self.use_hadoop:
            return HdfsTarget(self.destination)
        else:
            return LocalTarget(self.destination)

    def requires(self):
        import time

        return [ParetoAnalysisMean(self.use_hadoop, self.key_idx, self.value_idx, self.source, "{}_{}".format(self.__class__.__name__, time.strftime("%Y-%m-%d"))), CleanerHDFS(self.source)]

    def mapper(self, line):
        infos = line.split(MIGO_SEPARATOR_LEVEL1)
        if infos[1].count("!") > 0:
            yield "{}{}{}".format(infos[0], self.separator, infos[1]),
        else:
            yield "{}{}{}".format(infos[self.key_idx-1], self.separator, infos[self.value_idx-1]),

    def _run_reducer(self, stdin=sys.stdin, stdout=sys.stdout):
        def output(shop_id, mean):
            print >> stdout, "{}\t@{}".format(shop_id, mean)

        """Run the reducer on the hadoop node."""
        self.init_hadoop()
        self.init_reducer()

        #outputs = self._reduce_input(self.internal_reader((line[:-1] for line in stdin)), self.reducer, self.final_reducer)

        mean = None
        shop_id, sum, num = None, 0.0, 0

        for line in stdin:
            shop_id, value = line[1:-2].split(self.separator, 1)

            if value.count("!") == 1 and value.find("!") == 0:
                if mean != None:
                    output(shop_id, sum/num)

                mean = float(value[1:])
                sum, num = 0.0, 0
            else:
                shop_id, member_id, ordate, amt = value.split(MIGO_SEPARATOR_LEVEL1)

                if float(amt) > mean:
                    sum += float(amt)
                    num += 1

        output(shop_id, sum/num)

    #def reducer(self, key, values):
    #    pass

class ParetoAnalysis(luigi.hadoop.JobTask):
    use_hadoop = BooleanParameter()
    key_idx = IntParameter()
    value_idx = IntParameter()
    source = Parameter()
    destination = Parameter()

    def jobconfs(self):
        self.separator = "|"

        jcs = super(luigi.hadoop.JobTask, self).jobconfs()

        jcs.append("mapreduce.map.output.key.field.separator=%s" %self.separator)
        jcs.append("mapreduce.partition.keypartitioner.options=-k1,1")

        return jcs

    def output(self):
        if self.use_hadoop:
            return HdfsTarget(self.destination)
        else:
            return LocalTarget(self.destination)

    def requires(self):
        import time

        return [ParetoAnalysisHighMean(self.use_hadoop, self.key_idx, self.value_idx, self.source, "{}_{}".format(self.__class__.__name__, time.strftime("%Y-%m-%d"))), CleanerHDFS(self.source)]

    def mapper(self, line):
        infos = line.split(MIGO_SEPARATOR_LEVEL1)
        if infos[1].count("!") > 0 or infos["@"] > 0:
            yield "{}{}{}".format(infos[0], self.separator, infos[1]),
        else:
            yield "{}{}{}".format(infos[self.key_idx-1], self.separator, line),

    def _run_reducer(self, stdin=sys.stdin, stdout=sys.stdout):
        def output(line, tag):
            print >> stdout, "{}\t{}".format(line, tag)

        """Run the reducer on the hadoop node."""
        self.init_hadoop()
        self.init_reducer()

        #outputs = self._reduce_input(self.internal_reader((line[:-1] for line in stdin)), self.reducer, self.final_reducer)

        mean, high_mean = None, None
        shop_id, sum, num = None, 0.0, 0

        for line in stdin:
            shop_id, value = line[1:-2].split(self.separator, 1)

            if value.count("!") == 1 and value.find("!") == 0:
                mean = float(value[1:])
            elif value.count("@") == 1 and value.find("@") == 0:
                high_mean = float(value[1:])
            else:
                pass


if __name__ == "__main__": 
    luigi.run()
