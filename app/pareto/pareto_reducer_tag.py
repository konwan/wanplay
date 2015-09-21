#!/usr/bin/env python
import sys





##~~~~~~  tag customer  ~~~~~##
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
    tag()
