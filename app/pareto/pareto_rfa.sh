appPath=./app
inputFolder=/user/athena/data_prepare
outputFolder=/user/cindy/pareto

function mr(){
    local tmpinputFolder=$1
    local tmpoutputFolder=$2
    local mapper=$3      
    local reducer=$4

    #judge folder exist or not(hadoop no overwrite )
    hadoop fs -test -d ${tmpoutputFolder}
    if [ $? -eq 0 ]; then
         hadoop fs -rm -r ${tmpoutputFolder}
    fi

    # hadoop use
    # -file for uploading the folder
    hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
        -input "${tmpinputFolder}" \
        -output "${tmpoutputFolder}" \
        -file "${appPath}" \
        -mapper "${mapper}" \
        -reducer "${reducer}"
     #echo "int:${tmpinputFolder} out:${tmpoutputFolder}  map:${mapper} red:${reducer} argv:${argv}" 
}         


function mr_partitioner(){
    local tmpinputFolder1=$1
    local tmpinputFolder2=$2
    local tmpoutputFolder=$3
    local mapper=$4      
    local reducer=$5

    #judge folder exist or not(hadoop no overwrite )
    hadoop fs -test -d ${tmpoutputFolder}
    if [ $? -eq 0 ]; then
         hadoop fs -rm -r ${tmpoutputFolder}
    fi

    # hadoop use
    hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
        -Dmapreduce.map.output.key.field.separator=_  \
        -Dmapreduce.partition.keypartitioner.options=-k1,1 \
        -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner \
        -input "${tmpinputFolder1}" \
        -input "${tmpinputFolder2}" \
        -output "${tmpoutputFolder}" \
        -file "${appPath}" \
        -mapper "${mapper}" \
        -reducer "${reducer}"
}        



function mr_partitioner_multi(){
    local tmpinputFolder1=$1
    local tmpinputFolder2=$2
    local tmpinputFolder3=$3
    local tmpoutputFolder=$4
    local mapper=$5      
    local reducer=$6

    #judge folder exist or not(hadoop no overwrite )
    hadoop fs -test -d ${tmpoutputFolder}
    if [ $? -eq 0 ]; then
         hadoop fs -rm -r ${tmpoutputFolder}
    fi

    # hadoop use
    hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
        -Dmapreduce.map.output.key.field.separator=_  \
        -Dmapreduce.partition.keypartitioner.options=-k1,1 \
        -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner \
        -input "${tmpinputFolder1}" \
        -input "${tmpinputFolder2}" \
        -input "${tmpinputFolder3}" \
        -output "${tmpoutputFolder}" \
        -file "${appPath}" \
        -mapper "${mapper}" \
        -reducer "${reducer}"
}        






##############  ok ################

arg=1
mr ${inputFolder} ${outputFolder}/order_sum "${appPath}/pareto_mapper_data.py ${arg}" "${appPath}/pareto_reducer_data.py ${arg}"


arg=2
standard=0.0
mr ${outputFolder}/order_sum ${outputFolder}/mean "${appPath}/pareto_mapper_data.py ${arg}" "${appPath}/pareto_reducer_data.py ${arg} ${standard}"


arg=3
index=_
operation=!
mr ${outputFolder}/mean ${outputFolder}/part_mean "${appPath}/pareto_mapper_data.py ${arg} ${index} ${operation}" "cat"
mr_partitioner ${outputFolder}/order_sum ${outputFolder}/part_mean ${outputFolder}/high_mean "cat" "${appPath}/pareto_reducer_data.py ${arg} ${index} ${operation}"


arg=3
index=_
operation=.
mr ${outputFolder}/high_mean ${outputFolder}/part_high_mean "${appPath}/pareto_mapper_data.py ${arg} ${index} ${operation}" "cat"


arg=4
index=_
operation1=!
operation2=.
#mr_partitioner_multi ${outputFolder}/part_mean ${outputFolder}/part_high_mean ${outputFolder}/order_sum ${outputFolder}/tag "${appPath}/pareto_mapper_data.py ${arg} ${index} ${operation1} ${operation2}" "${appPath}/pareto_reducer_data.py ${arg}"
mr_partitioner_multi ${outputFolder}/part_mean ${outputFolder}/part_high_mean ${outputFolder}/order_sum ${outputFolder}/tagmap "cat" "${appPath}/pareto_mapper_data.py ${arg} ${index} ${operation1} ${operation2}"
mr ${outputFolder}/tagmap ${outputFolder}/tag "cat" "${appPath}/pareto_reducer_data.py ${arg}"

############# test ##################
