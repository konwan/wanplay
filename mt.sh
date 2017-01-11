# !/bin/sh

thread=2
curren_running=0

test(){
    i=$1
    sleep 5
    echo 1 >> aa  &&  echo "${i} done! "
}


date
for((i = 0 ;i < 5 ;i ++ ));
do
    if [ ${curren_running} -ge ${thread} ];then
        echo "too much"
        wait
        curren_running=0
    fi
    current_running=$(( ${current_running} + 1 ))
    echo "cr ${current_running} th ${thread}"
    echo "fork"
    test ${i} &
done

wait
wc -l aa
rm aa
date
