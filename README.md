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
