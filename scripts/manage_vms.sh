#!/bin/bash

create_clones() {
    local i
    for ((i=2; i<=$total_vm_count; i++))
    do
        clone_vm="${vm_prefix_name}${i}_${vm_suffix_name}"
        if ! virsh list --all | grep -q "\<${clone_vm}\>" # angle brackets for word boundaries
        then
            echo "cloning ${clone_vm}"
            virt-clone --connect=qemu:///system -o $base_vm -n $clone_vm --auto-clone
        else
            echo "already cloned ${clone_vm}"
        fi
    done
}

start_vms() {
    local i
    for ((i=1; i<=$total_vm_count; i++))
    do
        vm_name="${vm_prefix_name}${i}_${vm_suffix_name}"
        echo "starting ${vm_name}"
        virsh start $vm_name
    done
}

shutdown_vms() {
    local i
    for ((i=1; i<=$total_vm_count; i++))
    do
        vm_name="${vm_prefix_name}${i}_${vm_suffix_name}"
        echo "shutting down ${vm_name}"
        virsh shutdown $vm_name
    done
}

vm_prefix_name="vm"
vm_suffix_name="debian12"

# assume prefix1_suffix is already created
# shut it down for cloning
base_vm=${vm_prefix_name}1_${vm_suffix_name}

total_vm_count="$2"

case "$1" in
    clone)
        CMD=create_clones
        ;;
    start)
        CMD=start_vms
        ;;
    shutdown)
        CMD=shutdown_vms
        ;;
    *)
        exit
        ;;
esac

shift
$CMD "$@"
