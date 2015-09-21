#!/usr/bin/env python
import sys
import math
import numpy

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
       
### 0_0~.     14
### 0_no~$  5
### 0_no~no 5

def redsum():
    group, sum = "", 0
    group2, sum2 = "", 0
    all, total = "", 0
             
    for lines in sys.stdin:
        # result group 
        line = lines.strip().split("\t")
        if group != "" and group != line[0] : 
            print group + "\t" + str(sum)
            sum = 0
        sum += int(line[1])
        group = line[0]
    
        # col group 
        col = lines.strip().replace("~","\t").split("\t")
        if group2 != "" and group2 != col[0] : 
            print group2 + "~$\t" + str(sum2)
            sum2 = 0
        sum2 += int(col[2])
        group2 = col[0]

       
        # col group 
        alldata = lines.strip().replace("~","\t").replace("_","\t").split("\t")
        if all != "" and all != alldata[0] :
            print all + "_" + all + "~.\t" + str(total)
            total = 0
        total += int(alldata[3])
        all = alldata[0]

    print group + "\t" + str(sum) 
    print group2 + "~$\t" + str(sum2)
    print all + "_" + all + "~.\t" + str(total)



def redall():
    group, cnt, catcnt = "", 0, 0
    entropy, grouprate ,h =  0.0, 0.0, 0.0

    for line in sys.stdin:
        line = line.strip().split("\t")
       
        val = line[0].replace("~","_").strip().split("_")
                        

        if line[0].count(".") > 0:
            cnt = line[1]
            continue
        elif line[0].count("$") > 0 :
            catcnt = line[1]
            continue
        else :           
            if float(line[1])/float(catcnt) != 1 :
                entropy = -(float(line[1])/float(catcnt))*math.log( (float(line[1])/float(catcnt)) ,2)
         
            grouprate = float(catcnt)/float(cnt)
         
            if catcnt != cnt :
                h = -(grouprate*math.log(grouprate ,2))
            else :
                h = entropy 
            """
            if val[1] == val[2] :
                entropy = h
                grouprate = 1.0            
            """ 
  
            print val[0] + "~" + val[1]  + "_" + str(grouprate) + "_"  + str(entropy) + "_" + str(h)
            #print line[0] + "~~~_" + line[1] + "_" + str(catcnt) + "_" + str(cnt) + "_" + str(grouprate) + "_"  + str(entropy) + "_" + str(h) 
          
        entropy, grouprate ,h =  0.0, 0.0, 0.0


def mapcal():

    for line in sys.stdin:
        line = line.strip().split("_")
        print line[0] + "\t" + line[1] + "\t" + line[2] + "\t" + line[3]


def redcal():
    col, entropy, hv, p = "", 0.0, 0.0, 0.0
   
    for line in sys.stdin:
        line = line.strip().split("\t")
            
        if col != "" and col != line[0] :
            print col + "_" + str(p * entropy) + "_" + str(hv)
            entropy, hv, p =  0.0, 0.0, 0.0

        val = line[0].strip().split("~")               
        if val[0] == val[1] :
            hv += float(line[3])       
        else :
            hv = float(line[3])
        entropy += float(line[2])
        #hv = float(line[3])
        p = float(line[1])
        col = line[0]

    print col + "_" + str(p * entropy) + "_" + str(hv)
     


def mapall():
    info = 0.

    for line in sys.stdin:
        line = line.strip().replace("~","_").split("_")

        if line[0] == line[1] :
            info = line[3]
            continue
        print line[0] + "\t" + info + "\t" + line[2] + "\t" + line[3] 



def redfinal():
    col, entropy, hv, gain, igr = "", 0.0, 0.0, 0.0, 0.0

    for line in sys.stdin:
        line = line.strip().split("\t")
 
        if col != "" and col != line[0] :
            print col + "_" + str(float(line[1])-entropy) + "_" + str((float(line[1])-entropy)/hv)
            col, entropy, hv, gain, igr = "", 0.0, 0.0, 0.0, 0.0

        hv += float(line[3])
        entropy += float(line[2])
        col = line[0]
#    print col + "_" + str(entropy) + "_" + str(hv) + "_" + str(float(line[1])-entropy) + "_" + str((float(line[1])-entropy)/hv)
    print col + "_" + str(float(line[1])-entropy) + "_" + str((float(line[1])-entropy)/hv)

def numpytest():
    result = numpy.zeros((4, 3))
    i = 0 
    a = 1

    for line in sys.stdin:
        line = line.strip().replace("'","").split("_")      
        result[i, :] = [float(line[0]), float(line[1]), float(line[2])]
        i += 1
#    print result[numpy.argmax(result[:, a]), :]
    print result 
#print str(a) + "~" + str(b) + "~" + str(c)
if __name__ == "__main__" :
    input = ""
    if len(sys.argv) > 1 :
        input  = sys.argv[1]

    if input == '5' :
        map(input)

    elif input == '1' :
        redsum()

    elif input == '7' :
        redcol("~","!")

    elif input == '8' :
        redcol("_",".")

    elif input == '9' :
        redall()

    elif input == '10' :
        mapcal()
    
    elif input == '11' :
        redcal()

    elif input == '12' :
        mapall()

    elif input == '13' :
        redfinal()

    elif input == '14' :
        numpytest()

    else :
        print "bad guy"                              
