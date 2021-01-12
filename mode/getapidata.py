#!/usr/bin/env python
#coding=UTF-8

import os
import sys
import datetime
import json
import requests
import logging
import urllib2

def api_log(logs):
    logger = logging.getLogger('getdata')
    logger.setLevel(logging.DEBUG)

    #new a handler to write log
    fh = logging.FileHandler('Desktop/apidata/test.log')
    fh.setLevel(logging.DEBUG)

    #new a handle to print on console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    #format output
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    #add handler to logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    #record log
    logger.info(logs)
    #logger.debug("nono wrong")
    logger.removeHandler(ch)
    logger.removeHandler(fh)
    logging.shutdown()

if __name__ == "__main__":
    shop = sys.argv[1]
    store = sys.argv[2]
    caldate = sys.argv[3]

    
    #replacelist = ["(", ")", "!", "_", "@", "$", "%"] 
    #for i in replacelist:
    #    store.replace(i, "#migo#")

    tri_list = ["tri^BeeDees(百貨)", "tri^Ladies(加盟)", "tri^Ladies(百貨)", "tri^sloggi(百貨)", "tri^Tri(加盟)", "tri^Tri(百貨)", "tri^Tri(直營)", "tri^VALISERE(百貨)"]


    for i in tri_list :

        try :
            start = datetime.datetime.now()
            store_new = urllib2.quote(i)
            #url = "http://10.1.4.45:8000/lemon/starterdiy/memberallpaging/q/{}/{}/{}/L7D/0/0/0/0/0/0/100000000/0/".format(shop, store_new, caldate)
            url = "http://10.1.4.45:8000/lemon/starterdiy/memberallmongo/q/{}/{}/{}/L7D/0/0/0/0/0/0/9bb16b37-3165-485f-a54d-e3fb9a8a6596/".format(shop, store_new, caldate)

            data = json.loads(urllib2.urlopen(url).read())
            #data['store_id'] = data['store_id'].decode('unicode_escape')

            try :   
                f = open("Desktop/apidata/{}_{}.txt".format(store, data["count"]), 'w')
                f.write(str(data["member"]))
                f.close()
                end = datetime.datetime.now()
                api_msg = "{} takes {} seconds".format(i, (end - start).seconds) 
                api_log(api_msg)        
            except Exception, e:
                api_log(e)
        except Exception, e:
            api_log(e)


    """
    logger = logging.getLogger('getdata')  
    logger.setLevel(logging.DEBUG)  
  
    #new a handler to write log
    fh = logging.FileHandler('Desktop/apidata/test.log')  
    fh.setLevel(logging.DEBUG)  
  
    #new a handle to print on console
    ch = logging.StreamHandler()  
    ch.setLevel(logging.DEBUG)  
  
    #format output
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter)  
  
    #add handler to logger
    logger.addHandler(fh)  
    logger.addHandler(ch)  
  
    #record log 
    logger.info("foorb") 
    logger.debug("nono wrong") 
    """
