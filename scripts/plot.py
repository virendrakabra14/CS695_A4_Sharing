import matplotlib.pyplot as plt
import sys
import pathlib

# Define a function to parse the file and extract metrics for each interval
def parse_metrics(filename):
    interval_cpu_usage = []
    interval_pages_shared = []
    interval_pages_sharing = []
    interval_general_profit = []
    interval_numbers = []

    # Open the file
    with open(filename, 'r') as file:
        # Iterate over each line
        for line in file:
            # Strip whitespace from the line
            line = line.strip()

            # Check if the line starts with 'Interval'
            if line.startswith('Interval'):
                # If yes, extract the interval number
                parts = line.split(':')
                interval_number = int(parts[0].split()[1])
                interval_numbers.append(interval_number)

                # Extract the metrics
                cpu_usage = float(parts[1].split('=')[1])
                interval_cpu_usage.append(cpu_usage)

                # Continue reading the next lines for other metrics
                next_lines = file.readline().strip()
                while next_lines:
                    parts = next_lines.split(':')
                    interval_number = int(parts[0].split()[1])
                    if interval_number != interval_numbers[-1] :
                        interval_numbers.append(interval_number)
                    metric = parts[1].strip().split('=')
                    if metric[0] == 'average_cpu_usage':
                        interval_cpu_usage.append(float(metric[1]))
                    if metric[0] == 'pages_shared':
                        interval_pages_shared.append(float(metric[1]))
                    elif metric[0] == 'pages_sharing':
                        interval_pages_sharing.append(float(metric[1]))
                    elif metric[0] == 'general_profit':
                        interval_general_profit.append(float(metric[1]))
                    next_lines = file.readline().strip()

    return interval_numbers, interval_cpu_usage, interval_pages_shared, interval_pages_sharing, interval_general_profit

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

    if not MAKE_PLOTS_AGAINST_VMS:

        file1 = f'{metrics_folder}/{metrics_vs_interval_file_number}.log'
        interval_numbers, cpu_usage, pages_shared, pages_sharing, general_profit = parse_metrics(file1)

        # Plot each metric against interval
        plt.ioff()
        plt.plot(interval_numbers, cpu_usage, marker='o', label='CPU Usage')
        plt.xlabel('Interval')
        plt.ylabel('Average CPU Usage')
        plt.title('CPU Usage vs Interval')
        plt.grid(True)
        plt.savefig(f"{plots_folder}/cpu_usage_vs_interval.png")
        plt.close()

        plt.ioff()
        plt.plot(interval_numbers, pages_shared, marker='o', label='Pages Shared')
        plt.xlabel('Interval')
        plt.ylabel('Pages Shared')
        plt.title('Pages Shared vs Interval')
        plt.grid(True)
        plt.savefig(f"{plots_folder}/pages_shared_vs_interval.png")
        plt.close()

        plt.plot(interval_numbers, pages_sharing, marker='o', label='Pages Sharing')
        plt.xlabel('Interval')
        plt.ylabel('Pages Sharing')
        plt.title('Pages Sharing vs Interval')
        plt.grid(True)
        plt.savefig(f"{plots_folder}/pages_sharing_vs_interval.png")
        plt.close()

        plt.plot(interval_numbers, general_profit, marker='o', label='General Profit')
        plt.xlabel('Interval')
        plt.ylabel('General Profit')
        plt.title('General Profit vs Interval')
        plt.grid(True)
        plt.savefig(f"{plots_folder}/general_profit_vs_interval.png")
        plt.close()

    else:

        num_vms = NUM_VMS
        last_cpu = []
        last_shared = []
        last_gp = []
        last_sharing = []
        vms = range(1,num_vms+1)

        for vm in vms :
            file = f'{metrics_folder}/{vm}.log'
            interval_numbers, cpu_usage, pages_shared, pages_sharing, general_profit = parse_metrics(file)
            last_cpu.append(cpu_usage[-1])
            last_shared.append(pages_shared[-1])
            last_gp.append(general_profit[-1])
            last_sharing.append(pages_sharing[-1])

        vms = range(1,num_vms+1)
        # Plot each metric against vm
        plt.ioff()
        plt.plot(vms, last_cpu, marker='o', label='CPU Usage')
        plt.xlabel('VM')
        plt.ylabel('Average CPU Usage')
        plt.title('CPU Usage vs VM')
        plt.grid(True)
        plt.savefig(f"{plots_folder}/cpu_usage_vs_vm.png")
        plt.close()

        plt.ioff()
        plt.plot(vms, last_shared, marker='o', label='Pages Shared')
        plt.xlabel('VM')
        plt.ylabel('Pages Shared')
        plt.title('Pages Shared vs VM')
        plt.grid(True)
        plt.savefig(f"{plots_folder}/pages_shared_vs_vm.png")
        plt.close()

        plt.plot(vms, last_sharing, marker='o', label='Pages Sharing')
        plt.xlabel('VM')
        plt.ylabel('Pages Sharing')
        plt.title('Pages Sharing vs VM')
        plt.grid(True)
        plt.savefig(f"{plots_folder}/pages_sharing_vs_vm.png")
        plt.close()

        plt.plot(vms, last_gp, marker='o', label='General Profit')
        plt.xlabel('VM')
        plt.ylabel('General Profit')
        plt.title('General Profit vs VM')
        plt.grid(True)
        plt.savefig(f"{plots_folder}/general_profit_vs_vm.png")
        plt.close()
