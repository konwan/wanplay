#!/bin/sh


max=200

for i in `seq 1 $max`;
do
    sdt=$(date +"%Y-%m-%d %T")
    startdt=$(date -d "${sdt}" +%s)

    #sleep 1
    hadoop fs -put 20160527.txt /user/athena/newbalance/meb_attribute/20160526/20160526${i}.txt
    edt=$(date +"%Y-%m-%d %T")
    enddt=$(date -d "${edt}" +%s)

    cost_time=$(expr ${enddt} - ${startdt})
    echo "${sdt} 20160526${i}.txt ${edt},   ${cost_time} sec"
done
