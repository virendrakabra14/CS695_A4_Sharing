#!/bin/bash

while true; do
    # Read KSM statistics
    pages_shared=$(cat /sys/kernel/mm/ksm/pages_shared)
    pages_sharing=$(cat /sys/kernel/mm/ksm/pages_sharing)

    # Print current statistics
    echo "pages_shared: $pages_shared"
    echo "pages_sharing: $pages_sharing"

    # Sleep for some time before checking again
    sleep 1
done
