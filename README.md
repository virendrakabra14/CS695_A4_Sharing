# File-Structure

- `logs` store logs and plots of all experiments.
- `manual_programs` store programs that we used for understanding KSM working without VMs.
- `scripts` contain the main framework that we created and used for running and monitoring experiments:
    - `orchestrate.sh` is the main script for running experiments. It invokes other scripts as part of management and monitoring.
    - `manage_vms.sh` contain utilities for VM management: start-up, cloning, shut-down, workload-execution, etc.
    - `monitor_ksm.sh` is the monitoring script. It populates the log files with KSM system and per-process stats.
    - `make_plots.sh` invokes `plot.py` to plot interesting metrics parsed-out from the log files.

# Usage Instructions

# Requirements

- `sysstat` package for CPU monitoring
    - `mpstat` command is used from this package
- `sshpass` package for providing password with `ssh` command
    - store password in a file named `.password` in `a4` directory

## Commands
```bash
apt install sysstat
apt install sshpass
```

# Experiments without VMs: With manual programs

```bash
cd manual_programs
gcc mmap_arrays.c
./a.out # note the printed pid
```

In a separate terminal
```bash
# execute from inside manual_programs directory
bash ../scripts/monitor_ksm.sh <log-filename>.log 35 1 "" "<pid from above>"
# e.g. bash ../scripts/monitor_ksm.sh tmp.log 35 1 "" "11111"
```

To plot
```bash
# again, execute from inside manual_programs directory
python3 ../scripts/plot.py "." "<log-filename>" "<plot-dirname>" "0" "0"
# e.g. python3 ../scripts/plot.py "." "tmp" "tmp" "0" "0"
```

# Experiments with VMs

## Initial setup

```bash
# Check if system can run kvm
# Reference: https://www.tecmint.com/install-qemu-kvm-ubuntu-create-virtual-machines/
sudo apt update
sudo apt install cpu-checker -y
kvm-ok
# egrep -c '(vmx|svm)' /proc/cpuinfo

# Get qemu, virt-manager, etc.
sudo apt install qemu-kvm virt-manager virtinst libvirt-clients bridge-utils libvirt-daemon-system -y
```

## Setting up the first VM

We run Debian-12 in VMs for our experiments.

```bash
# Get the iso
wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.5.0-amd64-netinst.iso
```

We use `virt-manager` GUI for this setup. We use the downloaded image, and specify 512MB RAM, 4GB disk, and 1 CPU. This amount of memory and disk is recommended as [minimum in the installation guide](https://www.debian.org/releases/stable/amd64/ch03s04.en.html).

Inside virt-manager, we specify the disk to be used lazily (this is not a necessary step).

Please name this virtual machine as `vm1_debian12`. This is hard-coded within our VM management script. Subsequent clones will be auto-named as `vm<i>_debian12`.

During OS installation, we choose the (non-graphical) `Install` option from menu and opt only for `ssh` and basic utilities to be installed.

## Workloads

**NOTE**: follow these BEFORE any cloning (i.e., before running any VM experiments), so that this is already done in clones.

### Allowing `root` SSH into VMs

- Reference: [askubuntu](https://askubuntu.com/questions/511833/cant-ssh-in-as-root)
- Inside the first VM (`vm1_debian12` in our experiments)
    - Login as `root` user
    - Edit `/etc/ssh/sshd_config` (NOT `ssh_config`)
        - Uncomment `#PermitRootLogin ...` line
        - Change to `PermitRootLogin yes`
        - Save

### Installing workloads

#### stress-ng

- SSH into first VM as root (e.g. `ssh root@192.168.122.30`). IP can be obtained from virt-manager or from `get_ip` function in `scripts/manage_vms.sh`.
- Run
    ```bash
    apt update
    apt install stress-ng
    ```

## Run experiments

### Without workloads

```bash
cd scripts
# Arguments within [] are optional
sudo bash orchestrate.sh -m <max_vms> [-l <log_directory_path>] [-i <num_intervals>] [-d <interval_duration>] [-p <pages_to_scan>] [-s <sleep_millisecs>] [-c <vm_command>]
# e.g. sudo bash orchestrate.sh -m 3 -i 30 -d 60 -p 1000 -s 20
```

KSM daemon scans `pages_to_scan` pages every `sleep_millisecs` milliseconds.

This creates folder at `log_directory_path` and adds the logs. Default log folder name uses the current date and time.

### With workloads

#### stress-ng

Example usage
```bash
# change vm_username to root in manage_vms.sh

# turn off swap, and stress memory
# time for stress-testing should be comparable to i*d supplied to orchestrate.sh
# e.g. below monitoring for i*d=30*60=1800 seconds and stress-ng run for 900 seconds
sudo bash orchestrate.sh -m 3 -i 30 -d 60 -p 10000 -s 20 -c "swapoff -a; stress-ng -m 2 -t 900"
```

### Plot

To plot
```bash
chmod 777 <log_directory_path>
# Execute within scripts directory
bash make_plots.sh <number of vms> <log directory path>
# e.g. bash make_plots.sh 3 ../logs/logs_2024_04_19_14_26/
```

This creates a `plots` directory within the specified log directory.
