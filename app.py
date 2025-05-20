
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/cpu/fcfs", methods=["POST"])
def fcfs():
    data = request.get_json()
    print("Received data:", data)

    processes = data["processes"]

    # Convert keys to match expected format
    for p in processes:
        p["pid"] = p.pop("process")
        p["arrival_time"] = p.pop("arrivalTime")
        p["burst_time"] = p.pop("burstTime")

    processes.sort(key=lambda p: p["arrival_time"])
    time = 0
    gantt_chart = []
    completion_order = []
    total_tat = 0
    total_wt = 0

    for p in processes:
        start_time = max(time, p["arrival_time"])
        end_time = start_time + p["burst_time"]

        p["start_time"] = start_time
        p["completion_time"] = end_time
        p["turnaround_time"] = end_time - p["arrival_time"]
        p["waiting_time"] = p["turnaround_time"] - p["burst_time"]

        gantt_chart.append({
            "pid": p["pid"],
            "start": start_time,
            "end": end_time
        })

        completion_order.append(p["pid"])
        time = end_time
        total_tat += p["turnaround_time"]
        total_wt += p["waiting_time"]

    avg_tat = total_tat / len(processes)
    avg_wt = total_wt / len(processes)

    print("\nFinal FCFS Scheduling Results:")
    print(f"{'PID':<5} {'AT':<5} {'BT':<5} {'CT':<5} {'TAT':<5} {'WT':<5}")
    for p in processes:
        print(f"{p['pid']:<5} {p['arrival_time']:<5} {p['burst_time']:<5} {p['completion_time']:<5} {p['turnaround_time']:<5} {p['waiting_time']:<5}")
    print(f"Average Turnaround Time (TAT): {avg_tat:.2f}")
    print(f"Average Waiting Time (WT): {avg_wt:.2f}")

    return jsonify({
        "completion_order": completion_order,
        "gantt_chart": gantt_chart,
        "process_table": processes,
        "average_tat": avg_tat,
        "average_wt": avg_wt
    })


# ✅ SJF should NOT be indented
@app.route("/api/cpu/sjf", methods=["POST"])
def sjf():
    data = request.get_json()
    print("Received data:", data)

    processes = data["processes"]

    for p in processes:
        p["pid"] = p.pop("process")
        p["arrival_time"] = p.pop("arrivalTime")
        p["burst_time"] = p.pop("burstTime")

    n = len(processes)
    completed = 0
    current_time = 0
    visited = [False] * n
    gantt_chart = []
    completion_order = []
    total_tat = 0
    total_wt = 0

    while completed < n:
        idx = -1
        min_bt = float('inf')
        for i in range(n):
            if processes[i]["arrival_time"] <= current_time and not visited[i]:
                if processes[i]["burst_time"] < min_bt:
                    min_bt = processes[i]["burst_time"]
                    idx = i

        if idx == -1:
            current_time += 1
            continue

        p = processes[idx]
        start_time = current_time
        end_time = start_time + p["burst_time"]

        p["start_time"] = start_time
        p["completion_time"] = end_time
        p["turnaround_time"] = end_time - p["arrival_time"]
        p["waiting_time"] = p["turnaround_time"] - p["burst_time"]

        gantt_chart.append({
            "pid": p["pid"],
            "start": start_time,
            "end": end_time
        })
        completion_order.append(p["pid"])
        total_tat += p["turnaround_time"]
        total_wt += p["waiting_time"]

        visited[idx] = True
        completed += 1
        current_time = end_time

    avg_tat = total_tat / len(processes)
    avg_wt = total_wt / len(processes)

    print("\nFinal SJF Scheduling Results:")
    print(f"{'PID':<5} {'AT':<5} {'BT':<5} {'CT':<5} {'TAT':<5} {'WT':<5}")
    for p in processes:
        print(f"{p['pid']:<5} {p['arrival_time']:<5} {p['burst_time']:<5} {p['completion_time']:<5} {p['turnaround_time']:<5} {p['waiting_time']:<5}")
    print(f"Average Turnaround Time (TAT): {avg_tat:.2f}")
    print(f"Average Waiting Time (WT): {avg_wt:.2f}")

    return jsonify({
        "completion_order": completion_order,
        "gantt_chart": gantt_chart,
        "process_table": processes,
        "average_tat": avg_tat,
        "average_wt": avg_wt
    })

@app.route("/api/cpu/rr", methods=["POST"])
def round_robin():
    data = request.get_json()
    print("Received data:", data)

    quantum = data.get("quantum")
    processes = data["processes"]

    for p in processes:
        p["pid"] = p.pop("process")
        p["arrival_time"] = p.pop("arrivalTime")
        p["burst_time"] = p.pop("burstTime")

    n = len(processes)
    processes = sorted(processes, key=lambda x: x["arrival_time"])

    remaining_bt = [p["burst_time"] for p in processes]
    completion_time = [0] * n

    current_time = 0
    completed = 0
    queue = []
    visited = [False] * n
    gantt_chart = []

    # Initialize by adding all processes that arrive at time 0
    for i, p in enumerate(processes):
        if p["arrival_time"] == 0:
            queue.append(i)
            visited[i] = True

    if not queue:
        # If no process arrives at time 0, move time to first arrival
        current_time = processes[0]["arrival_time"]
        queue.append(0)
        visited[0] = True

    while completed < n:
        if not queue:
            # No ready process, jump time to next arriving process
            next_arrival = min([p["arrival_time"] for i, p in enumerate(processes) if not visited[i]])
            current_time = max(current_time, next_arrival)
            for i, p in enumerate(processes):
                if not visited[i] and p["arrival_time"] <= current_time:
                    queue.append(i)
                    visited[i] = True

        idx = queue.pop(0)
        p = processes[idx]

        start_time = current_time
        exec_time = min(quantum, remaining_bt[idx])
        current_time += exec_time
        remaining_bt[idx] -= exec_time

        gantt_chart.append({
            "pid": p["pid"],
            "start": start_time,
            "end": current_time
        })

        # Add any processes that have arrived by current_time and are not visited
        for i, proc in enumerate(processes):
            if not visited[i] and proc["arrival_time"] <= current_time:
                queue.append(i)
                visited[i] = True

        # If current process is not finished, put it back in queue
        if remaining_bt[idx] > 0:
            queue.append(idx)
        else:
            completion_time[idx] = current_time
            completed += 1

    # Calculate turnaround and waiting times
    total_tat = 0
    total_wt = 0
    for i, p in enumerate(processes):
        p["completion_time"] = completion_time[i]
        p["turnaround_time"] = p["completion_time"] - p["arrival_time"]
        p["waiting_time"] = p["turnaround_time"] - p["burst_time"]
        total_tat += p["turnaround_time"]
        total_wt += p["waiting_time"]

    avg_tat = total_tat / n
    avg_wt = total_wt / n

    print("\nFinal Round Robin Scheduling Results:")
    print(f"{'PID':<5} {'AT':<5} {'BT':<5} {'CT':<5} {'TAT':<5} {'WT':<5}")
    for p in processes:
        print(f"{p['pid']:<5} {p['arrival_time']:<5} {p['burst_time']:<5} {p['completion_time']:<5} {p['turnaround_time']:<5} {p['waiting_time']:<5}")
    print(f"Average Turnaround Time (TAT): {avg_tat:.2f}")
    print(f"Average Waiting Time (WT): {avg_wt:.2f}")

    return jsonify({
        "gantt_chart": gantt_chart,
        "completion_order": [g["pid"] for g in gantt_chart],
        "process_table": processes,
        "average_tat": avg_tat,
        "average_wt": avg_wt
    })

#new code for priority
@app.route("/api/cpu/priority", methods=["POST"])
def priority_scheduling():
    data = request.get_json()
    print("Received data for Priority Scheduling:", data)

    processes = data["processes"]

    for p in processes:
        p["pid"] = p.pop("process")
        p["arrival_time"] = p.pop("arrivalTime")
        p["burst_time"] = p.pop("burstTime")
        p["priority"] = p.pop("priority")

    # Sort by arrival time initially
    processes.sort(key=lambda x: x["arrival_time"])

    time = 0
    completed = 0
    n = len(processes)
    is_completed = [False] * n
    gantt_chart = []
    total_tat = 0
    total_wt = 0

    while completed < n:
        # Find all processes that have arrived and not completed
        ready_queue = [p for i, p in enumerate(processes) if p["arrival_time"] <= time and not is_completed[i]]

        if ready_queue:
            # Select process with highest priority (lowest number)
            current = min(ready_queue, key=lambda x: x["priority"])
            index = processes.index(current)

            start_time = time
            end_time = start_time + current["burst_time"]

            current["start_time"] = start_time
            current["completion_time"] = end_time
            current["turnaround_time"] = end_time - current["arrival_time"]
            current["waiting_time"] = current["turnaround_time"] - current["burst_time"]

            gantt_chart.append({
                "pid": current["pid"],
                "start": start_time,
                "end": end_time
            })

            total_tat += current["turnaround_time"]
            total_wt += current["waiting_time"]
            time = end_time
            is_completed[index] = True
            completed += 1
        else:
            # No process is ready, jump time forward
            time += 1

    avg_tat = total_tat / n
    avg_wt = total_wt / n

       # Formatted output for terminal
    print("\nFinal Priority Scheduling Results:")
    print(f"{'PID':<5}{'AT':<6}{'BT':<6}{'CT':<6}{'TAT':<6}{'WT':<6}")
    for p in processes:
        print(f"{p['pid']:<5}{p['arrival_time']:<6}{p['burst_time']:<6}{p['completion_time']:<6}{p['turnaround_time']:<6}{p['waiting_time']:<6}")
    print(f"Average Turnaround Time (TAT): {avg_tat:.2f}")
    print(f"Average Waiting Time (WT): {avg_wt:.2f}\n")
    
    return jsonify({
        "gantt_chart": gantt_chart,
        "average_tat": avg_tat,
        "average_wt": avg_wt
    })

#Memory managemnet FIFO
@app.route('/api/fifo', methods=['POST'])
def fifo_algorithm():
    data = request.get_json()
    frames = data.get('frames')
    reference_string = data.get('reference_string')

    if not frames or not reference_string:
        return jsonify({"error": "Invalid input"}), 400

    memory = []
    page_faults = 0
    history = []

    for page in reference_string:
        if page not in memory:
            if len(memory) < frames:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)
            page_faults += 1
        history.append(list(memory))  # Copy of current frame state

    return jsonify({
        "page_faults": page_faults,
        "frame_states": history
    })

