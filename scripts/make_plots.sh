#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: $0 <number of vms> <log directory path>"
    exit 1
fi

num_vms="$1"
log_dir_path="$2"

for ((i=1; i<=$num_vms; i++))
do
    python3 plot.py "$log_dir_path" "${log_dir_path}/plots/${i}" "$i" "0" "0" # last arg is dummy
done

python3 plot.py "$log_dir_path" "${log_dir_path}/plots/vms" "0" "1" "$num_vms" # "0" arg is dummy
