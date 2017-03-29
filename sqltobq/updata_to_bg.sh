#!/bin/bash

PATH_BASE=/home/gemini/gardener/custom/iot-hourly-data
PRJ=wscnair
FILENAME=${PRJ}_IoT_WiFi_StoreFunnelHourly.txt

to_log() {
  if [ -z "$1" ]
  then
    return
  fi
  time_log=`date +"%Y-%m-%d %H:%M:%S"`
  msg_log="$time_log - $1"
  echo $msg_log
}

to_log "start uploading to BQ..."

if [ ! -f "/home/migocn/sharedir/${FILENAME}.zip" ] ; then
    to_log "no file to do..."
    exit -1
fi

cp /home/migocn/sharedir/${PRJ}*.zip $PATH_BASE/data/
unzip $PATH_BASE/data/${FILENAME}.zip -d $PATH_BASE/data/

wc $PATH_BASE/data/${FILENAME}
iconv -f UTF-16LE -t UTF8 $PATH_BASE/data/${FILENAME} > $PATH_BASE/data/u8_${FILENAME}
wc $PATH_BASE/data/u8_${FILENAME}

gsutil cp $PATH_BASE/data/u8_${FILENAME} gs://bk_work/

bq --project_id watsons-1703 --nosync load --replace --max_bad_records 0 --skip_leading_rows 0 iot.IoT_WiFi_StoreFunnelHourly gs://bk_work/${FILENAME} \
apid,Status_Group,logdate:timestamp,hourly:integer,mac_cnt:integer,avg_seconds:float,avg_db:float,gda_regtime:timestamp,gda_lastupdate:timestamp

rm -f "$PATH_BASE/data/${FILENAME}"
rm -f "$PATH_BASE/data/u8_${FILENAME}"
rm -f "$PATH_BASE/data/${FILENAME}.zip"

sudo rm -f /home/migocn/sharedir/${FILENAME}.zip
gsutil rm gs://bk_work/u8_${FILENAME}
to_log "done uploading"
