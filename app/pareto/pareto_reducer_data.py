#!/usr/bin/env python
import sys


## cal order sum (mid,measure)
def sum():
    cus = ""
    sum = 0.0

    for line in sys.stdin: 
        line = line.strip().split("\t")
        
        if cus != "" and cus !=line[0]:
            print cus.replace("'","")+"\t"+ str(sum)
            sum = 0.0
        sum += float(line[1])
        cus = line[0]  
            
    print cus.replace("'","")+"\t"+ str(sum)  


## cal mean (store,measure)
def mean(standard):
    cus = ""
    sum = 0.0
    cnt = 0

    for line in sys.stdin:
        line = line.strip().split("\t")

        if cus != "" and cus != line[0]:       
            if cnt == 0:
                print cus + "\t" + str(cnt)
            else:
                print cus + "\t" + str(sum/cnt)       
            cnt = 0
            sum = 0.0
        
        if float(line[1]) > float(standard) :
            sum += float(line[1])
            cnt += 1

        cus = line[0]
    
    if cnt == 0:
        print cus + "\t" + str(cnt)
    else:
        print cus + "\t" + str(sum/cnt)
 

## cal high_mean (mid, measure)
def high_mean(index,operation) :
    cus = ""
    sum = 0.0
    cnt = 0
    standard =0.0 


    for line in sys.stdin :
        #get input
        line = line.strip().replace((index+operation), "").replace("_","\t").split("\t")

        #change store and set var default        
        if cus != "" and cus != line[0]:       
            if cnt == 0:
                print cus + "\t" + str(cnt)+"~" 
            else:
                print cus + "\t" + str(sum/cnt)       
            
            cnt = 0
            sum = 0.0
            standard = 0.0
        
        #get mean 
        if len(line) == 2 :
            standard = line[1] 
            cus = line[0]
            continue        
        
        #sum   
        if float(line[2]) > float(standard) :
            sum += float(line[2])
            cnt += 1

        #next record 
        cus = line[0]
    
    #last 
    if cnt == 0:
        print cus + "\t" + str(cnt)
    else:
        print cus + "\t" + str(sum/cnt)



## tag customer (mid,measure,mean,hmean)
def tag(): 
    for line in sys.stdin :
        line = line.strip().split("\t") 
                
        if float(line[1]) > float(line[3]) :
            print line[0] + "\tH"
#            print line[0] +"\t"+ str(line[1]) +"\t"+ str(line[2]) +"\t"+ str(line[3]) + "\tH"
        elif float(line[1]) < float(line[2]):
            print line[0] + "\tL"
#            print line[0] +"\t"+ str(line[1]) +"\t"+ str(line[2]) +"\t"+ str(line[3]) + "\tL"
        else :
            print line[0] + "\tM"
#            print line[0] +"\t"+ str(line[1]) +"\t"+ str(line[2]) +"\t"+ str(line[3]) + "\tM"
        



#################  main ###############################   
if __name__ == "__main__" :
    input = ""
    if len(sys.argv) > 1 :
        input  = sys.argv[1]   

    if input == '1' :
        sum()

    elif input =='2' :
        standard = sys.argv[2]

        mean(standard)

    elif input == '3' :
        index = sys.argv[2]
        operation = sys.argv[3]

        high_mean(index,operation)

    elif input == '4' :
        tag()

    else :
        print "bad guy"
