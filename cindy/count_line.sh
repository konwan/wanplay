#!/usr/bin/bash
filename="$1"

while read -r line
do
    name=$line
    rs_len=$($name | wc -c)

    echo "$name  $rs_len"
done < "$filename"
