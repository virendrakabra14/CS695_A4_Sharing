import matplotlib.pyplot as plt
import sys
import pathlib
import numpy as np
import os

def savefig(path):
    if pathlib.Path(path).is_file():
        print(f"WARNING: {path} already present. Skipping...")
        return
    plt.savefig(path)

# Define a function to parse the file and extract metrics for each interval
def parse_metrics(filename):
    ksm_metric_names = [
        "full_scans",
        "general_profit",
        "pages_shared",
        "pages_sharing",
        "pages_unshared",
        "pages_volatile",
    ]
    ksm_proc_metric_names = [
        "ksm_rmap_items",
        "ksm_merging_pages",
        "ksm_process_profit"
    ]

    vm_proc_pids = []
    vm_proc_prefixes = []

    interval_metrics = {}
    interval_metrics["interval_numbers"] = []
    interval_metrics["average_cpu_usage"] = []
    for e in ksm_metric_names:
        interval_metrics[e] = []

    interval_proc_metrics = {}
    interval_proc_metrics["vm_proc_pids"] = vm_proc_pids
    for e in ksm_proc_metric_names:
        interval_proc_metrics[e] = {}

    # Open the file
    with open(filename, 'r') as file:
        # Iterate over each line
        for line in file:
            # Strip whitespace from the line
            line = line.strip()

            # Check if the line starts with 'Interval'
            if line.startswith('Interval '):
                # If yes, extract the interval number
                parts = line.split(':')
                interval_number = int(parts[0].split()[1])
                interval_metrics["interval_numbers"].append(interval_number)

                # Extract cpu metric
                average_cpu_usage = float(parts[1].split('=')[1])
                interval_metrics["average_cpu_usage"].append(average_cpu_usage)

            # KSM metrics
            elif len(line.split('=')) == 2:
                metric = line.strip().split('=')
                if metric[0] in interval_metrics:
                    interval_metrics[metric[0]].append(float(metric[1]))
                elif metric[0] == "vm_pid_array":
                    vm_proc_pids = metric[1].split(' ')
                    interval_proc_metrics["vm_proc_pids"] = vm_proc_pids
                    vm_proc_prefixes = [f"/proc/{pid}/ksm_stat" for pid in vm_proc_pids]
                    for pid in vm_proc_pids:
                        for e in ksm_proc_metric_names:
                            interval_proc_metrics[e][pid] = []
                elif metric[0] in vm_proc_prefixes:
                    pid = metric[0].split('/')[2]
                    proc_metrics = metric[1].split(' ')
                    idx = 0
                    while idx < len(proc_metrics):
                        assert proc_metrics[idx] in ksm_proc_metric_names
                        interval_proc_metrics[proc_metrics[idx]][pid].append(
                            float(proc_metrics[idx+1])
                        )
                        idx += 2

    return interval_metrics, interval_proc_metrics

if __name__ == "__main__":

    """
    Expected usage: make_plots.sh
    """
    # Arguments
    metrics_folder = sys.argv[1]
    plots_folder = sys.argv[2] # is created if not present
    metrics_vs_interval_file_number = sys.argv[3]
    MAKE_PLOTS_AGAINST_VMS = int(sys.argv[4]) # this is only required True once for each experiment
    NUM_VMS = int(sys.argv[5])

    pathlib.Path(plots_folder).mkdir(exist_ok=True, parents=True)

    interval_numbers_key = "interval_numbers"
    vm_proc_pids_key = "vm_proc_pids"

    if not MAKE_PLOTS_AGAINST_VMS:

        file1 = f'{metrics_folder}/{metrics_vs_interval_file_number}.log'
        interval_metrics, interval_proc_metrics = parse_metrics(file1)

        # Plot each metric against interval
        for k, v in interval_metrics.items():
            if k == interval_numbers_key:
                continue

            plt.ioff()
            plt.plot(interval_metrics[interval_numbers_key], v, marker='o', label=k)
            plt.xlabel(interval_numbers_key)
            plt.ylabel(k)
            title = f'{k}-vs-{interval_numbers_key}'
            plt.title(title)
            plt.grid(True)
            plt.legend()
            savefig(f"{plots_folder}/{title}.png")
            plt.close()

        # Plot each proc metric against interval
        for k, v in interval_proc_metrics.items():
            if k == vm_proc_pids_key:
                continue

            plt.ioff()
            for pid, v2 in v.items():
                plt.plot(
                    interval_metrics[interval_numbers_key],
                    v2,
                    marker='o',
                    label=interval_proc_metrics[vm_proc_pids_key].index(pid)+1
                )
            plt.xlabel(interval_numbers_key)
            plt.ylabel(k)
            title = f'proc-{k}-vs-{interval_numbers_key}'
            plt.title(title)
            plt.grid(True)
            plt.legend()
            savefig(f"{plots_folder}/{title}.png")
            plt.close()

    else:

        num_vms = NUM_VMS
        last_interval_metrics = {}
        vms = range(1,num_vms+1)

        for vm in vms :
            file = f'{metrics_folder}/{vm}.log'
            interval_metrics, interval_proc_metrics = parse_metrics(file)
            for k, v in interval_metrics.items():
                if k == interval_numbers_key:
                    continue
                if k not in last_interval_metrics:
                    last_interval_metrics[k] = []
                last_interval_metrics[k].append(v[-1])

        vms = range(1,num_vms+1)
        # Plot each metric against vm
        for k, v in last_interval_metrics.items():
            plt.ioff()
            plt.plot(vms, v, marker='o', label=k)
            plt.xlabel('VM')
            plt.ylabel(k)
            title = f'{k}-vs-vms'
            plt.title(title)
            plt.grid(True)
            savefig(f"{plots_folder}/{title}.png")
            plt.close()

        reclaimed = np.array(last_interval_metrics["pages_sharing"])*4/1024
        pages_shared = np.array(last_interval_metrics["pages_shared"])*4/1024
        shared = reclaimed + pages_shared
        vms = np.array(vms)
        total_mem = vms*512
        plt.ioff()
        plt.plot(vms, total_mem, marker='s', label='VM Memory')
        plt.plot(vms, reclaimed, marker='^', label='Reclaimed')
        plt.plot(vms, shared, marker='o', label='Shared')
        plt.xlabel('Number of VMs')
        plt.ylabel('Memory (MB)')
        title = 'memory-vs-vms'
        plt.title(title)
        plt.grid(True)
        plt.legend()
        savefig(f"{plots_folder}/{title}.png")
        plt.close()

        shared = shared*100/total_mem
        reclaimed = reclaimed*100/total_mem
        diff = shared - reclaimed
        plt.ioff()
        plt.plot(vms, diff, marker='D', label='Shared - Reclaimed')
        plt.plot(vms, reclaimed, marker='^', label='Reclaimed')
        plt.plot(vms, shared, marker='o', label='Shared')
        plt.xlabel('Number of VMs')
        plt.ylabel('% VM Memory')
        title = 'percent-vs-vms'
        #plt.title(title)
        plt.grid(True)
        plt.legend()
        savefig(f"{plots_folder}/{title}.png")
        plt.close()

