#!/bin/sh
prid=$$
prname=$(basename $0)
lockdir="/home/cindy/cindy/lock"
cdir="-1"
cpid="-1"
cndir="-1"
cddir="-1"

function checkdir(){
    if test -d ${lockdir}; then
        cdir=1
    else
        cdir=0
    fi
}

function checkpid(){
    #if pgrep ${prname}; then
    if [ $(ps -ef |grep ${prname} |grep -v grep |wc -l) -gt 2 ]; then
        cpid=1
    else
        cpid=0
    fi
}

function newdir(){
    if mkdir ${lockdir}; then
        cndir=1
    else 
        cndir=0
    fi 
}

function deldir(){
    if rm -R ${lockdir}; then
        cddir=1
    else 
        cddir=0
    fi 
}

function newfile(){
    for i in $(seq 1 10);
    do
        sleep 100 
        echo "${i} Time is $(date +"%FT%T"), PID is ${prid}" >> cindy_${prid}.txt
    done
}

checkdir
checkpid

if [ ${cdir} -eq 0 ]  
then 
    # no lock no pid
    if [ ${cpid} -eq 0 ]  
    then
        echo "${prname} start running" >&2
        newdir
        newfile
        deldir
    #no folder with pid
    else
        echo "${prname} is running, but miss folder" >&2 
        newdir   
    fi
else
    #folder with no pid
    if [ ${cpid} -eq 0 ]  
    then
        echo "${prname} start running with folder" >&2
        newfile
        deldir
    #folder with pid
    else
        echo "${prname} already running, please wait" >&2     
    fi
fi
