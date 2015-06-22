#!/bin/sh

#############################################################################
##    Objectives: A sciprt to execute StarterDIY Athena TA Flow
#        Author: cindy
#  CreationDate: 2015/06/01
#         Usege: ./check.sh -s 'ordifen kg' -t i -p 3
#          Note: -d <date> -s <shop_id> -t <type i / h> -p <print_error_num> -f <folder>
#############################################################################


ftplist=
checktype=
print_error_cnt=5

while getopts "s:d:t:p:f:" opt; do
  case $opt in
    s)
      shop_id=$OPTARG
      ;;
    d)
      lasttadate=$OPTARG
      ;;
    t)
      type=$OPTARG
      ;;
    p)
      print_error_cnt=$OPTARG
      ;;
    f)
      dir=$OPTARG
      ;;
  esac
done

if [ -z "${shop_id}" ]; then
    ftplist=$(ls /data/diy-data)
else
    ftplist=${shop_id}
fi

if [ -z "${type}" ]; then
    checktype='--checkInc --checkHis'
elif [ ${type} == 'i' ]; then
    checktype='--checkInc'
else
    checktype='--checkHis'
fi

program=/root/tmp/cindy/datacheck_new.py

for i in ${ftplist};
do  
    python ${program} --shop_id ${i} --checkftp ${checktype} --checkmark --checkformat --checkdealdate --checkdealdetail --checkdir ${dir} --error_print_cnt ${print_error_cnt}
done;
