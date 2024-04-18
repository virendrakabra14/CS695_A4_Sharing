import matplotlib.pyplot as plt
import sys
import pathlib

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

    interval_metrics = {}
    interval_metrics["interval_numbers"] = []
    interval_metrics["average_cpu_usage"] = []
    for e in ksm_metric_names:
        interval_metrics[e] = []

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

    return interval_metrics

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

    pathlib.Path(plots_folder).mkdir(exist_ok=False, parents=True) # raise error if already present

    interval_numbers_key = "interval_numbers"

    if not MAKE_PLOTS_AGAINST_VMS:

        file1 = f'{metrics_folder}/{metrics_vs_interval_file_number}.log'
        interval_metrics = parse_metrics(file1)

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
            plt.savefig(f"{plots_folder}/{title}.png")
            plt.close()

    else:

        num_vms = NUM_VMS
        last_interval_metrics = {}
        vms = range(1,num_vms+1)

        for vm in vms :
            file = f'{metrics_folder}/{vm}.log'
            interval_metrics = parse_metrics(file)
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
            plt.savefig(f"{plots_folder}/{title}.png")
            plt.close()
