#!/bin/sh

#############################################################################
#    Objectives: A sciprt to execute ftp data to datanode
#        Author: cindy
#  CreationDate: 2015/06/15
#         Usage: ./test.sh -n meishilin -c others            ==>  change cfg and exec prog
#                ./test.sh -n meishilin -c others -s 2       ==>  only exec prog
#                ./test.sh -n meishilin -c others -s 3 -d 2  ==>  exec dn py
#          Note: -n <shop_id> -o <one_time_ip> -i <incremental_ip> -c <header/ transaction/ others> -s/-d <1-cfg 2-prog> 
#############################################################################
defaultothers=10.10.21.51
defaulttranx=10.10.21.53
step=
dnstep=
changecfg=
dnone=
dninc=
shop_id=
sedstr=
echostr=
checkdn=
while getopts "n:o:i:c:s:d:" opt; do
  case $opt in
    c)
      changecfg=$OPTARG
      ;;
    i)
      dninc=$OPTARG 
      ;;
    o)
      dnone=$OPTARG
      ;;
    n)
      shop_id=$OPTARG
      ;;
    s)
      step=$OPTARG
      ;;
    d)
      dnstep=$OPTARG
      ;;
  esac
done

if [ -z ${shop_id} ]; then
    echo "Empty shop_id - Terminated"
    exit 1
fi

sedstr="/shop_id/d;"
echostr="shop_id:\"${shop_id}\" "

if [ ! -z ${dnone} ]; then
    sedstr=${sedstr}" /datanodes_one_time/d;"
    echostr=${echostr}"\n""datanodes_one_time:\"'${dnone}'\" "
fi

if [ ! -z ${dninc} ]; then
    sedstr=${sedstr}" /datanodes_increamental/d;"
    echostr=${echostr}"\n""datanodes_increamental:\"'${dninc}'\" "
fi

user=$(whoami)
folder_cfg=/data/migo/folder_monitor/etc/
folder_prog=/data/migo/folder_monitor/bin/
#folder_cfg=/root/tmp/cindy/flow/etc/

function changecfg(){
    for entry in ${folder_cfg}*
    do
        if [[ ${entry} == *${changecfg}* ]];then
            sed "${sedstr}" ${entry} >> ${entry}tmp
            echo -e "${echostr}" >> ${entry}tmp

            mv ${entry} ${entry}rm
            mv ${entry}tmp ${entry}
            rm ${entry}rm
            chmod 755 ${entry}
        fi
    done
}

function execprog(){
    for entry in ${folder_prog}*
    do
        if [[ ${entry} == *${changecfg}* ]];then
            python ${entry}
        fi
    done
}

function checkdndata(){
    ip=$1
    type=$2
    #dirlist=$(IFS=',' read -a arr <<< "${shop_id}")
    #dirlist=$(echo ${shop_id} | cut -d ","  --output-delimiter=' ' -f 1-)
    datadir=/data/migo/starterDIY
    datacfg=/data/migo/athena/modules/folder_monitor/etc/

    ssh athena@${ip} "
        if [[ ${dnstep} == 1 ]]; then
            if [[ ${shop_id} == *','* ]] ; then
                ls ${datadir}/{${shop_id}}/*
            else
                ls ${datadir}/${shop_id}/*
            fi
        fi

        if [ ! -z ${dnstep} ]; then
            #sh -x /home/athena/cindy/luigi.sh
            sh /home/athena/cindy/athena.sh -n ${shop_id} -d ${dnstep} -c ${changecfg}
            exit 0
        fi    
     
        #if [[ ${type} == 'others' ]]; then
        #    echo /data/migo/starterDIY/${shop_id}/item
        #else
        #    echo /data/migo/starterDIY/${shop_id}/header
        #fi
        #du -h /data/migo/starterDIY/${shop_id}/*
    "
}

if [[ ${step} == 1 ]]; then
    changecfg
    cat ${folder_cfg}/*
    #execprog
elif [[ ${step} == 2 ]]; then
    execprog
else
    if [[ ! ${changecfg} == 'others' ]]; then
        checkdndata ${defaulttranx} ${changecfg} 
    fi
    checkdndata ${defaultothers} ${changecfg} 
fi


#1. su migo
#change etc 3 kinds cfg 
#excute ftp program

#2.su athena
#on datanode (52/ 53)
#check file ll /data/migo/starterDIY/mentor/* 

#change etc 3 kinds cfg
#excute dn program 
#/data/migo/athena/modules/folder_monitor/bin/folder_monitor_dn_others.py
