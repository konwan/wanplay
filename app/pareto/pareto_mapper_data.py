#!/usr/bin/env python
import sys



## deal data_prepare (store_mid, orderdate, amt) 
def get_order_sum():
    for line in sys.stdin:
        line = line.strip().split("\t")
        print (line[0] + "_" + line[1]),"\t", line[3] 


## deal store name (store, amt)
def get_store():
    for line in sys.stdin:
        line = line.strip().replace("\t", "_").split("_")
        print "{}\t{}".format(line[0], line[2])


## deal partitioner data (store_xx, amt)
def get_partitioner_data():
    for line in sys.stdin:
        if line.find("_") > -1:
            print line,
        else:
            print line.replace("\t", "_!\t", 1),


## deal partitioner data dynamic 
def get_partitioner_data_dyn(index,opration):
    for line in sys.stdin:
        if line.find(index) > -1:
            print line,
        else:
            print line.replace("\t", (index+opration+"\t"), 1),


## deal tag data (s1,mean,high_mean)
def get_tag_mean(index,operation1,opration2):
    store = ""
    cnt = 0
    mean = 0.0
    hmean=0.0

    for line in sys.stdin :
        cnt += 1 
        line = line.strip().replace((index+opration1), "").replace((index+opration2),"").replace("_","\t").split("\t")
        
        if store != "" and store!=line[0]:            
            cnt = 1
            mean = 0.0
            hmean = 0.0

        if cnt == 1 and len(line) == 2 :
            mean = line[1]           
#            print str(len(line)) + "\t" + str(cnt)+"\t" + store + "\t" + str(mean) + "\t" + str(hmean)
            store = line[0]
            continue 
        elif cnt == 2 and len(line) == 2 :
            hmean = line[1]           
            store = line[0]
            continue
        else : 
            print (line[0] + "_" + line[1]) + "\t" +line[2] + "\t" + str(mean) + "\t" + str(hmean) 

        #next record 
        store = line[0]
    
#    print (line[0] + "_" + line[1]) + "\t" +line[2] + "\t" + mean + "\t" + hmean 



######################################################

if __name__ == "__main__":
    if len(sys.argv) > 1 :
        input = sys.argv[1]

        if input == '1' :
            get_order_sum()

        elif input == '2' :
            get_store()

        elif input =='3' :
            index = sys.argv[2]
            opration = sys.argv[3]
 
            #get_partitioner_data()
            get_partitioner_data_dyn(index,opration)

        elif input == '4' :            
            index = sys.argv[2]
            opration1 = sys.argv[3]
            opration2 = sys.argv[4]

            get_tag_mean(index,opration1,opration2)

        else :
            print 'nonono~~~'

    else:
        print 'plz type par'


