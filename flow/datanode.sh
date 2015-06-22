#!/bin/sh
#sh cindy/athena.sh -n meishilin -d 2 -c others


step=
changecfg=
shop_id=
sedstr=
echostr=

while getopts "n:c:d:" opt; do
  case $opt in
    c)
      changecfg=$OPTARG
      ;;
    n)
      shop_id=$OPTARG
      ;;
    d)
      step=$OPTARG
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

function execprog(){
    for entry in ${folder_prog}*
    do
        if [[ ${entry} == *${changecfg}*  && ${entry} == *"dn"* ]] ; then
            echo python ${entry}
        fi
    done
}

function changecfg(){
    for entry in ${folder_cfg}*
    do
        if [[ ${entry} == *${changecfg}*  && ${entry} == *"dn"* ]] ; then
            sed "${sedstr}" ${entry} >> ${entry}tmp
            echo -e "${echostr}" >> ${entry}tmp

            mv ${entry} ${entry}rm
            mv ${entry}tmp ${entry}
            rm ${entry}rm
            chmod 755 ${entry}
        fi
    done
}

if [[ ${step}  == 1 ]]; then
    changecfg
    cat ${folder_cfg}*dn*.cfg
elif [[ ${step}  == 2 ]]; then
    execprog
else
    changecfg
    execprog
fi
