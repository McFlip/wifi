#!/bin/bash
# runs each simulator script over the other batches of traffic files
# this is for averaging the results
# stats files will concat to a csv file for import into spreadsheet
# graphs will be generated from spreadsheet

scriptPath="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for script in {aloha,slotted_aloha,csma}
do
  for i in {1,2}
  do
    for trafficfile in $scriptPath/$script/traffic$i/*
    do
      $( python $scriptPath/$script/$script.py -t $trafficfile -o $scriptPath/$script/output$i/`basename $trafficfile` ) &
    done
    wait
    echo "offered load,throughput" > $scriptPath/$script/catstat$i.csv
    cat $scriptPath/$script/output$i/*.stats >> $scriptPath/$script/catstat$i.csv
  done
done
