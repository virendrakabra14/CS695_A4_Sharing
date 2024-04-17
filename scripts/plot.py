import matplotlib.pyplot as plt
import sys 

folder = sys.argv[1]

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

# Example usage:
file1 = f'/home/advaid/SEM-8/CS695/CS695_A4_Sharing/logs/{folder}/1.log'
interval_numbers, cpu_usage, pages_shared, pages_sharing, general_profit = parse_metrics(file1)

# Plot each metric against interval
plt.ioff()
plt.plot(interval_numbers, cpu_usage, marker='o', label='CPU Usage')
plt.xlabel('Interval')
plt.ylabel('Average CPU Usage')
plt.title('CPU Usage vs Interval')
plt.grid(True)
plt.savefig("../plots/cpu_usage_vs_interval.png")
plt.close()

plt.ioff()
plt.plot(interval_numbers, pages_shared, marker='o', label='Pages Shared')
plt.xlabel('Interval')
plt.ylabel('Pages Shared')
plt.title('Pages Shared vs Interval')
plt.grid(True)
plt.savefig("../plots/pages_shared_vs_interval.png")
plt.close()

plt.plot(interval_numbers, pages_sharing, marker='o', label='Pages Sharing')
plt.xlabel('Interval')
plt.ylabel('Pages Sharing')
plt.title('Pages Sharing vs Interval')
plt.grid(True)
plt.savefig("../plots/pages_sharing_vs_interval.png")
plt.close()

plt.plot(interval_numbers, general_profit, marker='o', label='General Profit')
plt.xlabel('Interval')
plt.ylabel('General Profit')
plt.title('General Profit vs Interval')
plt.grid(True)
plt.savefig("../plots/general_profit_vs_interval.png")
plt.close()

num_vms = 3
last_cpu = [cpu_usage[-1]] 
last_shared = [pages_shared[-1]]
last_gp = [general_profit[-1]]
last_sharing = [pages_sharing[-1]]
vms = range(2,num_vms+1)

for vm in vms : 
    file = f'/home/advaid/SEM-8/CS695/CS695_A4_Sharing/logs/{folder}/{vm}.log'
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
plt.savefig("../plots/cpu_usage_vs_vm.png")
plt.close()

plt.ioff()
plt.plot(vms, last_shared, marker='o', label='Pages Shared')
plt.xlabel('VM')
plt.ylabel('Pages Shared')
plt.title('Pages Shared vs VM')
plt.grid(True)
plt.savefig("../plots/pages_shared_vs_vm.png")
plt.close()

plt.plot(vms, last_sharing, marker='o', label='Pages Sharing')
plt.xlabel('VM')
plt.ylabel('Pages Sharing')
plt.title('Pages Sharing vs VM')
plt.grid(True)
plt.savefig("../plots/pages_sharing_vs_vm.png")
plt.close()

plt.plot(vms, last_gp, marker='o', label='General Profit')
plt.xlabel('VM')
plt.ylabel('General Profit')
plt.title('General Profit vs VM')
plt.grid(True)
plt.savefig("../plots/general_profit_vs_vm.png")
plt.close()




