import random
import matplotlib.pyplot as plt

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None

def generate_processes(num_processes):
    return [
        Process(i, random.randint(0, 100), random.randint(1, 20), random.randint(1, 10))
        for i in range(num_processes)
    ]

def add_transient_process(processes):
    processes.append(Process(pid=67, arrival_time=50, burst_time=10, priority=1))

def reset_processes(processes):
    for p in processes:
        p.start_time = None
        p.completion_time = None
        p.waiting_time = None
        p.turnaround_time = None
        p.remaining_time = p.burst_time

def calculate_metrics(processes):
    total_waiting_time = sum(p.waiting_time or 0 for p in processes)
    total_turnaround_time = sum(p.turnaround_time or 0 for p in processes)
    num_processes = len(processes)

    avg_waiting_time = total_waiting_time / num_processes if num_processes > 0 else 0
    avg_turnaround_time = total_turnaround_time / num_processes if num_processes > 0 else 0

    transient_process = next((p for p in processes if p.pid == 67), None)
    transient_waiting_time = transient_process.waiting_time if transient_process else None
    transient_turnaround_time = transient_process.turnaround_time if transient_process else None

    return avg_waiting_time, avg_turnaround_time, transient_waiting_time, transient_turnaround_time

def plot_horizontal_gantt_chart(processes, title):
    fig, ax = plt.subplots()
    ax.set_xlabel('Time')
    ax.set_ylabel('Processes')
    ax.set_title(title)

    for p in processes:
        if p.start_time is not None:
            ax.barh(f'Process {p.pid}', p.burst_time, left=p.start_time, color='skyblue')
            ax.text(p.start_time + p.burst_time / 2, p.pid, f'P{p.pid}', ha='center', va='center')

    plt.xlim(0, max(p.completion_time for p in processes if p.completion_time is not None) + 10)
    plt.grid(axis='x')
    plt.show()

def schedule_fcfs(processes):
    current_time = 0
    for p in processes:
        current_time = max(current_time, p.arrival_time)
        p.start_time = current_time
        current_time += p.burst_time
        p.completion_time = current_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time

def schedule_sjf(processes):
    current_time = 0
    completed_processes = []
    while len(completed_processes) < len(processes):
        available_processes = [p for p in processes if p.arrival_time <= current_time and p not in completed_processes]
        if available_processes:
            p = min(available_processes, key=lambda x: x.burst_time)
            p.start_time = current_time
            current_time += p.burst_time
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed_processes.append(p)
        else:
            current_time += 1

def schedule_rr(processes, time_quantum):
    current_time = 0
    queue = [p for p in processes if p.arrival_time <= current_time]
    
    while queue:
        p = queue.pop(0)
        if p.start_time is None:
            p.start_time = current_time
        time_slice = min(p.remaining_time, time_quantum)
        current_time += time_slice
        p.remaining_time -= time_slice

        if p.remaining_time == 0:
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
        else:
            queue.append(p)
        
        queue.extend([np for np in processes if np.arrival_time <= current_time and np not in queue and np.remaining_time > 0])

def schedule_priority(processes):
    current_time = 0
    completed_processes = []
    
    while len(completed_processes) < len(processes):
        available_processes = [p for p in processes if p.arrival_time <= current_time and p not in completed_processes]
        if available_processes:
            p = min(available_processes, key=lambda x: x.priority)
            p.start_time = current_time
            current_time += p.burst_time
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed_processes.append(p)
        else:
            current_time += 1

def schedule_srtf(processes):
    current_time = 0
    completed_processes = []
    
    while len(completed_processes) < len(processes):
        available_processes = [p for p in processes if p.arrival_time <= current_time and p not in completed_processes]
        if available_processes:
            p = min(available_processes, key=lambda x: x.remaining_time)
            if p.start_time is None:
                p.start_time = current_time
            current_time += 1
            p.remaining_time -= 1
            
            if p.remaining_time == 0:
                p.completion_time = current_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                completed_processes.append(p)
        else:
            current_time += 1

def run_scheduling_algorithms():
    num_processes = 66
    processes = generate_processes(num_processes)
    add_transient_process(processes)
    processes.sort(key=lambda p: p.arrival_time)

    algorithms = {
        "FCFS": schedule_fcfs,
        "SJF": schedule_sjf,
        "Round Robin": schedule_rr,
        "Priority": schedule_priority,
        "SRTF": schedule_srtf
    }

    metrics = {}
    for name, func in algorithms.items():
        reset_processes(processes)
        if name == "Round Robin":
            func(processes, time_quantum=4)
        else:
            func(processes)
        
        plot_horizontal_gantt_chart(processes, f"{name} Horizontal Gantt Chart")
        metrics[name] = calculate_metrics(processes)

    print("\n--- Comparison of Scheduling Algorithms ---")
    print(f"{'Algorithm':<25}{'Avg Waiting Time':<20}{'Avg Turnaround Time':<20}{'Transient Waiting Time':<25}{'Transient Turnaround Time':<25}")
    for name, vals in metrics.items():
        avg_waiting_time = vals[0] if vals[0] is not None else 0.0
        avg_turnaround_time = vals[1] if vals[1] is not None else 0.0
        transient_waiting_time = vals[2] if vals[2] is not None else 0.0
        transient_turnaround_time = vals[3] if vals[3] is not None else 0.0
        
        print(f"{name:<25}{avg_waiting_time:<20.2f}{avg_turnaround_time:<20.2f}{transient_waiting_time:<25.2f}{transient_turnaround_time:<25.2f}")

    print("\n--- Conclusion ---")
    conclusions = {
        "FCFS": "Simple to implement but can have high waiting time, especially for short processes.",
        "SJF": "Minimizes waiting time for short processes but can lead to starvation for long processes.",
        "Round Robin": "Fairly distributes CPU time but can have high waiting time if the time quantum is not optimal.",
        "Priority": "Processes with higher priority are scheduled first, which can cause starvation for low-priority processes.",
        "SRTF": "Efficient for minimizing waiting time but complex to implement and can cause starvation for long processes."
    }
    for name, conclusion in conclusions.items():
        print(f"{name}: {conclusion}")

if __name__ == "__main__":
    run_scheduling_algorithms()
