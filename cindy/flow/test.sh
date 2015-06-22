#!/bin/sh

#############################################################################
#    Objectives: A sciprt to execute StarterDIY Athena TA Flow
#        Author: RungChi
#  CreationDate: 2015/03/06
#          Note: -n <shop_id> -o -i -c<header/ transaction/ others>
#############################################################################

changecfg=
dnone=
dninc=
shop_id=
sedstr=
echostr=
while getopts "n:o:i:c:" opt; do
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
place=/root/tmp/cindy/flow/
#folder_cfg=/data/migo/folder_monitor/etc/
folder_cfg=/root/tmp/cindy/flow/etc/

export shop_id

su - migo -c "whoami"
whoami
#su - migo -c "ls /data/migo/"
#sudo -u migo sh -s "$@" <<"EOF"
su - migo  <<"EOF"
        #echo "nonono${shop_id}"
        #for i in $(echo a b c)
        #do
	#    ls /data/migo/folder_monitor/etc/folder_monitor_ftp_header.cfg 
        #    echo ${i}
        #done
        #place=/home/migo
        sh /data/migo/folder_monitor/etc2/migo.sh 
	exit
EOF
changecfg(){
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

changesample(){
    sed "${sedstr}" migo.cfg >> ${place}/tmp.cfg
    echo -e "${echostr}" >> ${place}/tmp.cfg
    mv ${place}/migo.cfg ${place}/migo2.cfg
    mv ${place}/tmp.cfg ${place}/migo.cfg
    rm ${place}/migo2.cfg
    chmod 755 ${place}/migo.cfg
}
#changecfg
#export shop_id
#ssh-copy-id -i id_rsa.pub 10.10.21.53
#ssh root@10.10.21.53 '
#hostname
#pwd
#echo ${shop_id}
#ls'
#./migo.sh

#ips="10 11 12"
#for ip in $(echo ${ips});

#1. su migo
#change etc 3 kinds cfg 
#excute ftp program

#2.su athena
#on datanode (52/ 53)
#check file ll /data/migo/starterDIY/mentor/* 

#change etc 3 kinds cfg
#excute dn program 
#/data/migo/athena/modules/folder_monitor/bin/folder_monitor_dn_others.py
