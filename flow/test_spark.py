#!/usr/bin/env python
#coding=UTF-8

import pyspark
from pyspark import SparkConf, SparkContext

if __name__ == "__main__":
    r1 = [(1,"a1"), (2,"b2"), (3,"c3"), (4,"rrrr")]
    r2 = [(1,"a4"), (2,"b5"), (3,"c6")]
    r3 = [(1,"a7"), (2,"b8")]

    #data1.cogroup(data2, data3)
    cf = SparkConf().setAppName("test")
    sc = SparkContext(conf = cf)

    rd1 = sc.parallelize(r1)
    rd2 = sc.parallelize(r2)
    rd3 = sc.parallelize(r3)

    print rd1.count()
    print rd2.count()
    print rd3.count()
