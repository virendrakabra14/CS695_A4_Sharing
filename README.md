# Running experiments

## With manual programs
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

# Workloads

## Allowing `root` SSH into VMs

- NOTE: do this BEFORE any cloning, so that this is already done in clones
- Reference: [askubuntu](https://askubuntu.com/questions/511833/cant-ssh-in-as-root)
- Inside the first VM (`vm1_debian12` in our experiments)
    - Login as `root` user
    - Edit `/etc/ssh/sshd_config` (NOT `ssh_config`)
        - Uncomment `#PermitRootLogin ...` line
        - Change to `PermitRootLogin yes`
        - Save

## Installing workloads

### stress-ng

- SSH into first VM as root (e.g. `ssh root@192.168.122.30`)
- Run
    ```bash
    apt update
    apt install stress-ng
    ```

## Experiments with VMs 

```bash
cd scripts 
# Arguments within [] are optional
sudo bash orchestrate.sh -m <max_vms> [-l <log_directory_path>] [-i <num_intervals>] [-d <interval_duration>] [-p <pages_to_scan>] [-s <sleep_millisecs>] [-c <vm_command>]
```

This creates folder at <log_directory_path> and adds the logs  

To plot 
```bash
chmod 777 <log_directory_path> 
#Execute within scripts directory
bash make_plots.sh <number of vms> <log directory path> 
```

## Running workloads

### stress-ng

Example usage
```bash
# change vm_username to root in manage_vms.sh

# turn off swap, and stress memory
# time for stress-testing should be comparable to i*d supplied to orchestrate.sh
# e.g. below monitoring for i*d=30*60=1800 seconds and stress-ng run for 900 seconds
sudo bash orchestrate.sh -m 3 -i 30 -d 60 -p 10000 -s 20 -c "swapoff -a; stress-ng -m 2 -t 900"
```
