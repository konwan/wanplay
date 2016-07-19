#!/bin/sh

# Example script that uses lock files to avoid concurrent writes
# TODO: loads more validation and error handling!
#
# www.DonaldSimpson.co.uk
# 25th May 2011

setup_lockfile(){
    # set name of this program's lockfile:
    MY_NAME=$(basename $0)
    WHOAMI=$(whoami)
    LOCKFILE=/tmp/lock.${MY_NAME}.${WHOAMI}.lockfile

    # MAX_AGE is how long to wait until we assume a lock file is defunct
    # scary stuff, with loads of scope for improvement...
    # could use fuser and see if there is a process attached/not?
    # maybe check with lsof? or just bail out?
    MAX_AGE=1

    echo "My lockfile name is ${LOCKFILE}"
    sleep 1
}

check_lock(){
    # Check for an existing lock file
    while [ -f ${LOCKFILE} ]
    do
        # A lock file is present
        pid=$(cat ${LOCKFILE})
        pid_count=$(ps aux | grep ${pid} | grep ${MY_NAME} | wc -l)

        if [ ${pid_count} -gt 0 ]; then
            echo "Warning - still running - ${pid}"
            exit 2
        else
            echo "WARNING: found and removing old lock file...${LOCKFILE} - ${pid}"
            rm -f ${LOCKFILE}
        fi
    done
}

create_lock(){
    # ok to carry on... create a lock file - quickly ;-)
    echo $$ > ${LOCKFILE}
    # check we managed to make it ok...
    if [ ! -f ${LOCKFILE} ]; then
        echo "Unable to create lockfile ${LOCKFILE}!"
        exit 1
    fi

    echo "Created lockfile ${LOCKFILE}"
}

cleanup_lock(){
    echo "Cleaning up... "
    rm -f ${LOCKFILE}
    if [ -f ${LOCKFILE} ]; then
        echo "Unable to delete lockfile ${LOCKFILE}!"
        exit 1
    fi

    echo "Ok, lock file ${LOCKFILE} removed."
}
