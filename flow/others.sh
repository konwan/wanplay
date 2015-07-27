#!/bin/sh
#sh cindy/athena.sh -n meishilin -d 2 -t -c others
#sh /home/athena/cindy/athena.sh -n 'ablejeans' -d 3 -c transaction -g '5,3,2' -t 20150722

step=
changetype=
shop_id=
sedstr=
echostr=
tadate=$(date +'%Y%m%d')
tag=0

while getopts "n:c:d:t:g:" opt; do
  case $opt in
    c)
      changetype=$OPTARG
      ;;
    n)
      shop_id=$OPTARG
      ;;
    d)
      step=$OPTARG
      ;;
    t)
      tadate=$OPTARG
      ;;
    g)
      tag=$OPTARG
      ;;
  esac
done

if [ -z ${shop_id} ]; then
    echo "Empty shop_id - Terminated"
    exit 1
fi

sedstr="/shop_id/d;"
echostr="shop_id:\"${shop_id}\" "

user=$(whoami)
folder_cfg=/data/migo/athena/modules/folder_monitor/etc/
folder_prog=/data/migo/athena/modules/folder_monitor/bin/
check_prog=/home/athena/cindy/others.py



function execprog(){
    for entry in ${folder_prog}*
    do
        if [[ ${entry} == *${changetype}*  && ${entry} == *"dn"* ]] ; then
            python ${entry}
        fi
    done
}

function changecfg(){
    for entry in ${folder_cfg}*
    do
        if [[ ${entry} == *${changetype}*  && ${entry} == *"dn"* ]] ; then
            sed "${sedstr}" ${entry} >> ${entry}tmp
            echo -e "${echostr}" >> ${entry}tmp

            mv ${entry} ${entry}rm
            mv ${entry}tmp ${entry}
            rm ${entry}rm
            chmod 755 ${entry}
        fi
    done
}

function checkdata(){
    tmp=$(echo ${shop_id} | sed 's/,/ /g')
    if [[ ${changetype} == 'others' || -z ${changetype} ]]; then
       for shop in ${tmp}
       do
           python ${check_prog} ${shop} "ProjectBasicInfo" "others" "\"\"" "\"\""
       done
    fi

    if [[ ${changetype} == 'transaction' ]]; then
        for shop in ${tmp}
        do
            python ${check_prog} ${shop} "ProjectTagInfo_${shop}" "ta" ${tadate} ${tag}
        done
    fi
}



if [[ ${step}  == 1 ]]; then
    changecfg
    cat ${folder_cfg}*dn*.cfg
elif [[ ${step}  == 2 ]]; then
    execprog
elif [[ ${step}  == 3 ]]; then
    checkdata
fi
