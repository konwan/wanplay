#!/usr/bin/env python

import sys
sys.path.append("/data/migo/athena/lib")

from athena_variable import *
from athena_luigi import *

import re, math
from datetime import datetime

import luigi, luigi.hadoop, luigi.hdfs
 

"""
sunny  hot     high    FALSE   no
sunny  hot     high    TRUE    no
overcast        hot     high    FALSE   yes
rainy   mild    high    FALSE   yes
rainy   cool    normal  FALSE   yes
"""
class Pivot(MigoLuigiHdfs):

    keep_temp = luigi.BooleanParameter()
    inputcol = luigi.IntParameter(default=5, config_path={"section": "entropy", "name": "idx-column"})

    def start(self):
	pass

    def extra_confs(self):
        return ["mapreduce.map.output.key.field.separator=_", "mapreduce.partition.keypartitioner.options=-k1,1"]  

    def remove_files(self):
	if not self.keep_temp:
            return [self.dest]
        else:
            return []

    def requires(self):
        if self.use_hadoop:
            return CleanerHDFS(self.src)
        else:
            return CleanerLocal(self.src)

    def output(self):
        if self.use_hadoop:
            return luigi.hdfs.HdfsTarget(self.dest, format=luigi.hdfs.PlainDir)
        else:
            return luigi.LocalTarget(self.dest)
   
      
    def reducer(self, key, values):  
         pass
    
    def _run_reducer(self, stdin=sys.stdin, stdout=sys.stdout):
        def output(line, sep, val):  
            print >> stdout, "{}{}{}".format(line, sep, val)

        self.init_hadoop()
        self.init_reducer()

        group, sum = "", 0
        group2, sum2 = "", 0
        all, total = "", 0

        for lines in stdin:
            # result group           
            line = lines.strip().replace("'","").split(MIGO_SEPARATOR_LEVEL1)               
            if group != "" and group != line[0] : 
        	output(group, MIGO_SEPARATOR_LEVEL1, str(sum))
                sum = 0
            sum += int(line[1])
            group = line[0]
             
            # col group 
            col = lines.strip().replace("'","").replace("~",MIGO_SEPARATOR_LEVEL1).split(MIGO_SEPARATOR_LEVEL1)
            if group2 != "" and group2 != col[0] :
	        output(group2, "~$" + MIGO_SEPARATOR_LEVEL1, str(sum2))
                sum2 = 0
            sum2 += int(col[2])
            group2 = col[0]
                              
            # col group sum
            alldata = lines.strip().replace("'","").replace("~",MIGO_SEPARATOR_LEVEL1).replace("_",MIGO_SEPARATOR_LEVEL1).split(MIGO_SEPARATOR_LEVEL1)               
            if all != "" and all != alldata[0] :
	        output(all + "_" + all, "~." + MIGO_SEPARATOR_LEVEL1, str(total))
                total = 0
            total += int(alldata[3])
            all = alldata[0]
                 
        output(group, MIGO_SEPARATOR_LEVEL1, str(sum))
        output(group2, "~$" + MIGO_SEPARATOR_LEVEL1, str(sum2))     
        output(all + "_" + all, "~." + MIGO_SEPARATOR_LEVEL1, str(total))                    
    
    def mapper(self, line): 
        i = int(self.inputcol)-1 
        output, cnt = "", 1
 
        line = line.strip().split(MIGO_SEPARATOR_LEVEL1)
        for idx,val in enumerate(line):
            if i == idx :
                output = "0"
                val = "0"
            else :
                output = str((idx+1))
            yield "{}_{}~{}".format(output, val, line[i]), str(cnt)
       




"""
0_0~.   14
0_0~$   14
0_0~no  5
0_0~yes 9
1_1~.   14
1_overcast~$    4
1_overcast~yes  4
"""
class Sumcnt(MigoLuigiHdfs):

    keep_temp = luigi.BooleanParameter()

    def start(self):
	self.tmp = self.tmp_path("pivot")

    def extra_files(self):
	return []

    def extra_confs(self):         
        return ["mapreduce.map.output.key.field.separator=_", "mapreduce.partition.keypartitioner.options=-k1,1"] 

    def remove_files(self):
	if not self.keep_temp:
            return [self.dest]
        else:
            return []

    def requires(self):
        return Pivot(use_hadoop=self.use_hadoop, src=self.src, dest=self.tmp, keep_temp=self.keep_temp)


    def output(self):
        if self.use_hadoop:
            return luigi.hdfs.HdfsTarget(self.dest, format=luigi.hdfs.PlainDir)
        else:
            return luigi.LocalTarget(self.dest)
        
    def reducer(self, key, values): 
        pass

    def _run_reducer(self, stdin=sys.stdin, stdout=sys.stdout):
        def output(line):  
            print >> stdout, "{}".format(line)
  
        self.init_hadoop()
        self.init_reducer()

        cnt, catcnt = 0, 0

        for line in stdin:
            line = line.strip().replace("'","").split(MIGO_SEPARATOR_LEVEL1)
            val = line[0].replace("~","_").strip().split("_")
            
            if line[0].count(".") > 0:
                cnt = line[1]
                continue
            elif line[0].count("$") > 0 :
                catcnt = line[1]
                continue
            else :       
                output(val[0] + "_" + val[1]  + "_" + str(cnt) + "_"  + str(catcnt) + "_" + line[1])        
   
    def mapper(self, line):
        key, value = line.strip().replace("'","").split(MIGO_SEPARATOR_LEVEL1)        
        yield "{}".format(key), str(value) 

"""
0_0_14_14_5
0_0_14_14_9
1_overcast_14_4_4
1_rainy_14_5_2
1_rainy_14_5_3
1_sunney_14_5_2
1_sunney_14_5_3
"""
class Cal(MigoLuigiHdfs):

    keep_temp = luigi.BooleanParameter()

    def start(self):
        self.tmp = self.tmp_path("sumcnt")

    def extra_files(self):
        return []

    def extra_confs(self):
        return ["mapreduce.map.output.key.field.separator=_", "mapreduce.partition.keypartitioner.options=-k1,1"]

    def remove_files(self):
        if not self.keep_temp:
            return [self.dest]
        else:
            return []

    def requires(self):
        return Sumcnt(use_hadoop=self.use_hadoop, src=self.src, dest=self.tmp, keep_temp=self.keep_temp)

    def output(self):
        if self.use_hadoop:
            return luigi.hdfs.HdfsTarget(self.dest, format=luigi.hdfs.PlainDir)
        else:
            return luigi.LocalTarget(self.dest)

    def reducer(self, key, values):
        pass

    def _run_reducer(self, stdin=sys.stdin, stdout=sys.stdout):
        def output(line):  
            print >> stdout, "{}".format(line)
        
        self.init_hadoop()
        self.init_reducer()

        col, group, entropy, hv, p = "", "", 0.0, 0.0, 0.0    

        for line in stdin:
            line = line.strip().replace("'","").split("_")  

            entropy += -(float(line[3])/float(line[2])) * (float(line[4])/float(line[3])*math.log((float(line[4])/float(line[3])) ,2))              
            if  group != line[1] :
                hv += -(float(line[3])/float(line[2])*math.log((float(line[3])/float(line[2])) ,2))

            col = line[0]
            group = line[1]
            if col == group :
                hv = entropy
       
        output(col + "_" + str(entropy) + "_" + str(hv) )  


    def mapper(self, line):
        key = line.strip().replace("'","")
        yield "{}".format(key), 


"""
0_0.940285958671_0.0
1_0.693536138896_1.57740628285
2_0.911063393012_1.55665670746
3_0.788450457308_1.0
4_0.892158928262_0.985228136034
"""
class EntropyHv(MigoLuigiHdfs):   
         
    keep_temp = luigi.BooleanParameter()
    allcolumn = luigi.IntParameter(default=5, config_path={"section": "entropy", "name": "all-column"})
    inputcol = luigi.IntParameter(default=5, config_path={"section": "entropy", "name": "idx-column"})
 
    def start(self):
        self.tmp = self.tmp_path("cal")
             
    def extra_files(self):
        return []

    def extra_confs(self):
        return ["mapreduce.map.output.key.field.separator=_", "mapreduce.partition.keypartitioner.options=-k1,1"]
    
    def remove_files(self):
        if not self.keep_temp:
            return [self.dest]
        else:
            return []
    
    def requires(self):
        return Cal(use_hadoop=self.use_hadoop, src=self.src, dest=self.tmp, keep_temp=self.keep_temp)

    def output(self):
        if self.use_hadoop:
            return luigi.hdfs.HdfsTarget(self.dest, format=luigi.hdfs.PlainDir)
        else:
            return luigi.LocalTarget(self.dest)
    
    def reducer(self, key, values):
        pass

    def _run_reducer(self, stdin=sys.stdin, stdout=sys.stdout):
        def output(line):
            print >> stdout, "{}".format(line)

        self.init_hadoop()
        self.init_reducer()

        col, gain, igr = "", 0.0, 0.0
        entropy, hv = 0.0, 0.0 

        for line in stdin:
            line = line.strip().replace("'","").split("_") 
            
            if line.count(".") > 0 :
	        entropy = float(line[2])
		hv = float(line[3])
		continue
            else : 
                try : 
                    gain = entropy - float(line[2])
		    igr  = gain / float(line[3])
		    col = line[0]
                except Exception as e :
                    output(MIGO_STAMP_FOR_ERROR_RECORD + "\t" + col + "\t" + e.message)
          
        output(col + "_" + str(gain) + "_" + str(igr))        

    def mapper(self, line):                                                                         
        key, v1, v2 = line.strip().split("_") 
        idx = int(self.allcolumn) + 1

        if key == "0" :           
            for i in range(1, idx):    
                if i == int(self.inputcol) :                                                      
                    continue                                                               
                else :                                                       
                    yield "{}_{}_{}_{}".format( i, ".", v1, v2), 
        else :                                                                             
            yield "{}_{}_{}_{}".format( key, key, v1, v2), 



##############################  main   #######################################
if __name__=='__main__':
    luigi.run()
