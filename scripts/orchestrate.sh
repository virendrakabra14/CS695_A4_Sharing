#!/bin/bash

# Function to create file and parent directories
mkfileP() {
    # https://stackoverflow.com/a/24666836/17786040
    mkdir -p "$(dirname "$1")" || exit 1
    touch "$1"
}

# Function to start a given number of VMs
start_vms() {
    local num_vms=$1
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

# Main experiment function
run_experiment() {
    local max_vms="$1"
    local num_intervals="$2"
    local interval_duration="$3"
    local log_directory_path="$4"

    for ((i=1; i<=$max_vms; i++))
    do
        echo "Running experiment with $i VMs"

        log_file_path="${log_directory_path}/${i}.log"
        if [ -e $log_file_path ]
        then
            echo "ERROR: $log_file_path exists"
            exit 1
        fi
        mkfileP $log_file_path

        echo "i=$i while start"
        start_vms $i
        bash monitor_ksm.sh $log_file_path $num_intervals $interval_duration
        echo "i=$i while shutdown"
        shutdown_vms $i
    done
}

# Check if all required arguments are provided
if [ $# -ne 4 ]; then
    echo "Usage: $0 <max_vms> <num_intervals> <interval_duration> <log_directory_path>"
    exit 1
fi

# Run experiment with provided arguments
shutdown_vms "$1"
run_experiment "$@"
