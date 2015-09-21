#!/usr/bin/env python
import sys
import math

##############      1_overcast~yes    14
## cal order sum (mid,measure)
def map(input):
    i = int(input)-1
    output = ""
    cnt = 0

    for line in sys.stdin:
        line = line.strip().split("\t")
        cnt = 1

        for idx,val in enumerate(line):
            if i == idx :
                output = "0"
                val = "0"   
            else :
                output = str((idx+1))
            output += "_" + val + "~" + line[i] + "\t" + str(cnt)
            print output   
       
###############      1_overcast~yes    2    
def redcolcat():

    group, cnt = "", 0
    
    for line in sys.stdin:
        
        line = line.strip().split("\t")
        
        if group != "" and group != line[0] :
            print group + "\t" + str(cnt)
            cnt = 0
        cnt += 1
        group = line[0]

    print group + "\t" + str(cnt)


############## (~,!)     1_overcast!      4
############## (_,.)     1_.      14   	
def redcol(rep, out):
    group, sum = "", 0
    
    for line in sys.stdin:      
        line = line.strip().replace(rep,"\t").split("\t")
#        print line[0] + "~~~~~~~~" + line[1] + "@@@@@@" + line[2]
        if group != "" and group != line[0] :
            print group + "~" + out + "\t" + str(sum)
            sum = 0
        sum += int(line[2])
        group = line[0]

    print group + "~" + out +"\t" + str(sum)



### 0~.     14
### 0_no~!  5
### 0_no~no 5

def redall():
    group, cnt, catcnt = "", 0, 0
    entropy, grouprate ,h =  0.0, 0.0, 0.0

    for line in sys.stdin:
        line = line.strip().split("\t")
       
        if line[0].count(".") > 0:
            cnt = line[1]
            continue
        elif line[0].count("!") > 0 :
            catcnt = line[1]
            continue
        else :
            if float(line[1])/float(catcnt) != 1 :
                entropy = -(float(line[1])/float(catcnt))*math.log( (float(line[1])/float(catcnt)) ,2) 
            grouprate = float(catcnt)/float(cnt) 
            h = -(grouprate*math.log(grouprate ,2))      

            val = line[0].replace("~","_").strip().split("_")
             
            if val[1] == val[2] :
                entropy = h 
                grouprate = 1.0          

            print val[0] + "~" + val[1]  + "_" + str(grouprate) + "_"  + str(entropy) + "_" + str(h) 
            #print line[0] + "_" + line[1] + "_" + str(catcnt) + "_" + str(cnt) + "_" + str(grouprate) + "_"  + str(entropy) + "_" + str(h) 
           
        


def mapcal():

    for line in sys.stdin:
        line = line.strip().split("_")
        print line[0] + "\t" + line[1] + "\t" + line[2] + "\t" + line[3]



def redcol():
    col, entropy, hv = "", 0.0, 0.0
 
    for line in sys.stdin:
        line = line.strip().split("\t")
        if col != "" and col != line[0] :
            print col + "_" + str(entropy) + "_" + str(hv)
            entropy, hv =  0.0, 0.0

        entropy += float(line[1]) * float(line[2])
        hv += float(line[3])
        col = line[0]

    print col + "_" + str(entropy) + "_" + str(hv)






if __name__ == "__main__" :
    input = ""
    if len(sys.argv) > 1 :
        input  = sys.argv[1]

    if input == '5' :
        map(input)

    elif input == '6' :
        redcolcat()

    elif input == '7' :
        redcol("~","!")

    elif input == '8' :
        redcol("_",".")

    elif input == '9' :
        redall()

    elif input == '10' :
        mapcal()
    
    elif input == '11' :
        redcol()

    else :
        print "bad guy"                              
