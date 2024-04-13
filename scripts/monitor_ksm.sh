#!/bin/bash

log_file="$1"
truncate -s0 $log_file # empty the log file

num_intervals="$2"
interval_duration="$3"
echo "num_intervals=$num_intervals" >> $log_file
echo "interval_duration=$interval_duration" >> $log_file

get_ksm_sys_stat() {
    local arg="$1"
    local stat=$(cat /sys/kernel/mm/ksm/$arg)
    echo $stat
}

ksm_sys_params=("pages_shared" "pages_sharing" "general_profit")

for ((i=1; i<=$num_intervals; i++))
do
    sleep $interval_duration
    for param in "${ksm_sys_params[@]}"
    do
        stat=$(get_ksm_sys_stat $param)
        echo "Interval $i: $param=$stat" >> $log_file
    done
done
