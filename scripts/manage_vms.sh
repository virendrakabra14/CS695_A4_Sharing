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

get_ip() {
    # assume VMs have bridged networking setup
    local vm_name="$1"
    local vm_mac_address
    local vm_ip_address=""
    while [ -z $vm_ip_address ]
    do
        vm_mac_address=$(virsh -q domiflist ${vm_name} | awk '{ print $5 }')
        vm_ip_address=$(virsh -q net-dhcp-leases default --mac ${vm_mac_address} | awk '{ print $5 }' | awk -F'/' '{ print $1 }')
    done
    echo $vm_ip_address # captured by caller
}

get_vm_ips() {
    local -n ip_arr="$1"
    local i

    ip_arr=()
    for ((i=1; i<=$total_vm_count; i++))
    do
        vm_name="${vm_prefix_name}${i}_${vm_suffix_name}"
        ip_arr+=($(get_ip ${vm_name}))
    done
}

execute_command_in_vms() {
    local command="$2"
    echo "$command"
    local vm_ip_arr
    local password_file_path="../.password" # hard-coded
    local vm_username="vmuser"

    # get vm ips
    get_vm_ips vm_ip_arr
    echo "${vm_ip_arr[@]}"

    local i

    for ((i=1; i<=$total_vm_count; i++))
    do
        local vm_name="${vm_prefix_name}${i}_${vm_suffix_name}"
        echo "executing '$command' on ${vm_name}"
        local zero_based_idx=$(($i-1))

        # ssh and execute command in background
        sshpass -f "$password_file_path" ssh "${vm_username}@${vm_ip_arr[$zero_based_idx]}" "$command" #&
    done
}

vm_prefix_name="vm"
vm_suffix_name="debian12"

# assume prefix1_suffix is already created
# shut it down for cloning
base_vm=${vm_prefix_name}1_${vm_suffix_name}

total_vm_count="$2"

for ((i=1; i<=$#; i++))
do
    echo "Argument $i: ${!i}"
done

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
    exec)
        CMD=execute_command_in_vms
        ;;
    *)
        exit
        ;;
esac

shift
$CMD "$@"
