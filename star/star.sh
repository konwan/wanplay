#!/bin/sh

#############################################################################
#    Objectives: A sciprt to push KPI to backend's DB
#        Author: cindy
#  CreationDate: 2015/08/05
#          Note: -s <starting_date> -e <ending_date> -n <shop_id> -t <number of thread>
#       Example: ./et_api.sh -s 20140101 -t 4 -e 20140131 -n nestletw
#############################################################################

start_dt=
end_dt=
thread=4

while getopts "s:e:n:t:r:" opt; do
  case $opt in
    s)
      start_dt=$OPTARG
      ;;
    e)
      end_dt=$OPTARG
      ;;
    t)
      thread=$OPTARG
      ;;
  esac
done

if [ -z "${start_dt}" ] || [ -z "${end_dt}" ]; then
    echo "Empty parameters - ${start_dt}, ${end_dt}"
    exit 1
fi



#TIMESTR='2011-11-24'
#TM=`date +%s -d "$TIMESTR"`
#TM=$(($TM - 30 * 24 * 3600))
#TIMESTR=`date +%Y-%m-%d -d@"$TM"`
#echo $TIMESTR


start_timestamp=$(date -d "${start_dt}" +%s)
end_timestamp=$(date -d "${end_dt}" +%s)

for timestamp in $(seq ${start_timestamp} 86400 ${end_timestamp});
do
    cal_date=$(date -d @${timestamp} +%Y%m%d)
    this_month=$(date -d @${timestamp} +'%Y%m')

    next_timestamp=$(expr ${timestamp} + 86400)
    next_month=$(date -d @${next_timestamp} +'%Y%m')

    period=$(echo ${cal_date} | cut -c7-8)
    half=$(expr ${period} / 2)


    if [ "${this_month}" != "${next_month}" ]; then
        start=$(date +%Y-%m-%d:%H:%M:%S)
        starttime=$(date +%s)
        python star.py star ${this_month}01 ${this_month}${half}
        sleep 1
        end=$(date +%Y-%m-%d:%H:%M:%S)
        endtime=$(date +%s)
        echo "${this_month}${half}  start at  ${start}  end at  ${end}  cost $(expr ${endtime} - ${starttime})" >> /root/star.log
        #echo "$(expr $(expr $(expr ${endtime} - ${starttime}) / 60))"
        #echo $(awk "BEGIN{printf "%.2f\n", " $(expr $(expr ${endtime} - ${starttime})" / "2") }")
        #$(echo "scale=4;$sum/$subjects"|bc)
        #awk 'BEGIN{printf "%.2f\n",'$a'/'$b'}'

        start=$(date +%Y-%m-%d:%H:%M:%S)
        starttime=$(date +%s)
        #sleep 2
        python star.py star ${this_month}$(expr ${half} + 1) ${this_month}${period}
        end=$(date +%Y-%m-%d:%H:%M:%S)
        endtime=$(date +%s)
        echo "${this_month}${period}  start at  ${start}  end at  ${end}  cost $(expr ${endtime} - ${starttime})" >> /root/star.log
        #echo "${cal_date} ${this_month} ${next_month} ${period}"
        #echo "cost $(expr ${endtime} - ${starttime})"

    fi

done

