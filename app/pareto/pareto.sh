appPath=./app
inputFolder=/user/athena/data_prepare
outputFolder=/user/cindy/polato

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
    hadoop jar /usr/bin/hadoop-streaming.jar \
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
    hadoop jar /usr/bin/hadoop-streaming.jar \
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




##############  ok ################
#mr ${inputFolder} ${outputFolder}/order_sum "${appPath}/pareto_mapper_data.py" "${appPath}/pareto_reducer_order_sum.py"
#mr ${outputFolder}/order_sum ${outputFolder}/mean "${appPath}/pareto_mapper_store.py" "${appPath}/pareto_reducer_mean.py"
mr_partitioner ${outputFolder}/order_sum ${outputFolder}/mean ${outputFolder}/order_mean "${appPath}/pareto_mapper_mean.py" "${appPath}/pareto_reducer_high_mean.py"

mr ${outputFolder}/mean ${outputFolder}/par_mean "${appPath}/pareto_mapper_high_mean.py '_' '!'" "cat"
mr ${outputFolder}/high_mean ${outputFolder}/par_high_mean "${appPath}/pareto_mapper_high_mean.py '_' '@'" "cat"
mr_partitioner ${outputFolder}/order_sum ${outputFolder}/par_mean ${outputFolder}/par_high_mean "${appPath}/pareto_mapper_tag.py" "${appPath}/pareto_reducer_tag.py"

############# test ##################
#mr_partitioner ${outputFolder}/testmean ${outputFolder}/testhighmean ${outputFolder}/order_mean "${appPath}/pareto_mapper_mean.py" "${appPath}/pareto_reducer_high_mean.py"
#hadoop fs -ls ${outputFolder}/order_mean
#hadoop fs -cat ${outputFolder}/order_mean/part-*


#mr_partitioner ${outputFolder}/order_sum ${outputFolder}/mean ${outputFolder}/order_mean "cat" "cat"

#mr_partitioner ${outputFolder}/order_sum ${outputFolder}/mean ${outputFolder}/high_mean "cat" "${appPath}/pareto_reducer_high_mean.py"


#mr ${inputFolder} ${outputFolder}/order_sum "${appPath}/pareto_mapper_data.py" "${appPath}/pareto_reducer_order_sum.py"
#mr ${outputFolder}/order_sum ${outputFolder}/averagemin "${appPath}/pareto_mapper_store.py" "${appPath}/pareto_reducer_average.py"

#arg=$(hadoop fs -cat ${outputFolder}/averagemin/part-*)
#mr ${outputFolder}/averagemin ${outputFolder}/averagehmin "" "pareto_reducer_average.py ${arg}"

