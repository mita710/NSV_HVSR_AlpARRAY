#!/bin/sh -x

ls derived*.txt > files

cat files|\
while read line

do

avg=`cat $line |awk '{sum+=$NF; count++} END {print sum/count}'`
lat=`cat $line | head -1 | awk '{print $1}'`
lon=`cat $line | head -1 | awk '{print $2}'`

echo $lat $lon $avg >> values.txt

done
