#!/bin/bash

# Function to create file and parent directories
mkfileP() {
    # https://stackoverflow.com/a/24666836/17786040
    local filepath="$1"
    mkdir -p "$(dirname $filepath)" || exit 1
    touch $filepath
}

# Function to start a given number of VMs
start_vms() {
    local num_vms=$1
    local i # important to use local keyword, otherwise changes i value in caller
    for ((i=1; i<=$num_vms; i++))
    do
        bash manage_vms.sh clone $i
    done
    bash manage_vms.sh start $num_vms
    sleep 10
}

# Function to shutdown all VMs
shutdown_vms() {
    local num_vms=$1
    bash manage_vms.sh shutdown $num_vms
    sleep 10
}

# Function to update system ksm parameters
update_ksm_parameters() {
    local pages_to_scan="$1"
    local sleep_millisecs="$2"

    echo $pages_to_scan > "/sys/kernel/mm/ksm/pages_to_scan"
    echo $sleep_millisecs > "/sys/kernel/mm/ksm/sleep_millisecs"
}

restore_ksm_param() {
    echo "$1" > "/sys/kernel/mm/ksm/$2"
}

get_vm_pids() {
    local max_vms="$1"
    local -n pid_arr="$2"

    pid_arr=()
    local i

    for ((i=1; i<=$max_vms; i++))
    do
        vm_name="${vm_prefix_name}${i}_${vm_suffix_name}"
        pid_arr+=($(cat /var/run/libvirt/qemu/${vm_name}.pid))
    done
}

# Main experiment function
run_experiment() {
    local max_vms="$1"
    local num_intervals="$2"
    local interval_duration="$3"
    local log_directory_path="$4"
    local pages_to_scan="$5"
    local sleep_millisecs="$6"
    local i

    # run ksmd
    echo 1 > "/sys/kernel/mm/ksm/run"
    # update ksm system parameters for this experiment
    update_ksm_parameters $pages_to_scan $sleep_millisecs

    for ((i=1; i<=$max_vms; i++))
    do
        echo "Running experiment with $i VMs"

        local log_file_path="${log_directory_path}/${i}.log"
        if [ -e $log_file_path ]
        then
            echo "ERROR: $log_file_path exists"
            exit 1
        fi
        mkfileP $log_file_path

        # start vms (cloning happens here if required)
        start_vms $i

        # get vm pids
        local vm_pid_array
        get_vm_pids $i vm_pid_array

        # monitor ksm stats
        bash monitor_ksm.sh $log_file_path $num_intervals $interval_duration "${vm_pid_array[@]}"

        # shutdown
        shutdown_vms $i
    done
}

# Unset mandatory arguments
unset -v max_vms

# Set default values for optional arguments
num_intervals=30
interval_duration=60
pages_to_scan=100
sleep_millisecs=200
log_directory_path="../logs/logs_$(date '+%Y_%m_%d_%H_%M')"

# global variables
vm_prefix_name="vm"
vm_suffix_name="debian12"

# Function to print usage directions
usage() {
    echo "Usage: $0 -m max_vms [-l log_directory_path] [-i num_intervals=$num_intervals] [-d interval_duration=$interval_duration] [-p pages_to_scan=$pages_to_scan] [-s sleep_millisecs=$sleep_millisecs]"
}

# Parsing command line options
# leading colon: handle unknown args in code, and
# m: means option m requires a value
while getopts ":m:i:d:l:p:s:" opt; do
    case $opt in
        m) max_vms="$OPTARG" ;;
        l) log_directory_path="$OPTARG" ;;
        i) num_intervals="$OPTARG" ;;
        d) interval_duration="$OPTARG" ;;
        p) pages_to_scan="$OPTARG" ;;
        s) sleep_millisecs="$OPTARG" ;;
        \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
    esac
done
shift $((OPTIND -1))

# Check if all required arguments are provided
if [ -z $max_vms ] || [ -z $log_directory_path ]
then
    usage >&2
    echo 'Missing -m or -l' >&2
    exit 1
fi

# Run experiment with provided arguments
shutdown_vms $max_vms
run_experiment $max_vms $num_intervals $interval_duration $log_directory_path $pages_to_scan $sleep_millisecs

# Restore changed ksm system parameters to default
restore_ksm_param 100 "pages_to_scan"
restore_ksm_param 200 "sleep_millisecs"
