#!/bin/bash

log_file="$1"
truncate -s0 $log_file # empty the log file

num_intervals="$2"
interval_duration="$3"
command_executed_in_vms="$4"
vm_pid_array=("${@:5}")
echo "num_intervals=$num_intervals" >> $log_file
echo "interval_duration=$interval_duration" >> $log_file
echo "command_executed_in_vms='$command_executed_in_vms'" >> $log_file
echo "vm_pid_array=${vm_pid_array[*]}" >> $log_file

log_ksm_sys_params() {
    echo "[BEGIN] Logging ksm system parameters" >> $log_file
    local ksm_sys_params=("/sys/kernel/mm/ksm/"*)
    local param_file
    for param_file in "${ksm_sys_params[@]}"
    do
        local param_name=$(basename "$param_file")
        local param_value=$(cat "$param_file")
        echo "$param_name=$param_value" >> $log_file
    done
    echo "[END] Logging ksm system parameters" >> $log_file
}

get_ksm_sys_stat() {
    local arg="$1"
    local stat=$(cat /sys/kernel/mm/ksm/$arg)
    echo $stat
}

get_ksm_proc_stat() {
    local pid="$1"
    local stat=$(cat /proc/${pid}/ksm_stat | tr '\n' ' ')
    echo $stat
}

# at the start, log all ksm system parameters
log_ksm_sys_params

# then log once per interval

ksm_sys_params=("pages_shared" "pages_sharing" "general_profit")

for ((i=1; i<=$num_intervals; i++))
do
    # Log average cpu usage. This blocks for $interval_duration, so no extra sleep needed
    # https://stackoverflow.com/a/9229396/17786040
    average_cpu_usage=$(mpstat $interval_duration 1 | grep -A 5 '%idle' | tail -n 1 | awk -F ' ' '{print 100 -  $ 12}'a)
    echo "Interval $i: average_cpu_usage=$average_cpu_usage" >> $log_file

    # Log ksm system metrics
    for param in "${ksm_sys_params[@]}"
    do
        stat=$(get_ksm_sys_stat $param)
        echo "Interval $i: $param=$stat" >> $log_file
    done

    # Log per vm ksm metrics
    for vm_pid in "${vm_pid_array[@]}"
    do
        stat=$(get_ksm_proc_stat "$vm_pid")
        echo "Interval $i: /proc/$vm_pid/ksm_stat=$stat" >> $log_file
    done
done
