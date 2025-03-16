import algorithmdata as ad
import ready_queue as rq

def fcfs(processes, t_cs):
    data = ad.AlgorithmData("FCFS")
    queue = rq.ReadyQueue("FCFS")

    # Initially add all processes to the queue.
    for process in processes:
        queue.add(process)
    active = None
    t = 0
    print(f"time {t}ms: Simulator started for FCFS {queue}")

    while queue.size() > 0:
        process = queue.pop()

        # Handle process arrival.
        if process.get_state() == "None":
            t = handle_arrival(process, active, queue, data, t_cs)

        # Dispatch a ready process if no process is active.
        elif active is None and process.get_state() == "ready":
            t, active = dispatch_process(process, active, queue, data, t_cs)

        # Process is running; handle CPU burst completion.
        elif process.get_state() == "running":
            t, active, terminated = handle_running(process, queue, data, t, t_cs)
            if terminated:
                continue  # Process terminated; go to next iteration.

        # Process has been waiting (finishing I/O); update its state.
        elif process.get_state() == "waiting":
            t = handle_waiting(process, queue, t_cs, active)

        # If process is ready but another is active, update its sort time.
        elif process.get_state() == "ready" and active:
            handle_ready_with_active(process, active, queue, t_cs)

    print(f"time {t}ms: Simulator ended for FCFS {queue}")
    data.total_run_time = t
    print(data)


def handle_arrival(process, active, queue, data, t_cs):
    """Handle a process that is just arriving in the system."""
    process = set_ready(process, active, t_cs)
    t = process.get_arrival_time()
    process.set_ready_time(t)
    queue.add(process)
    if process.get_type():
        data.num_cpu_processes += 1
    else:
        data.num_io_processes += 1
    if t < 10000:
        print(f"time {t}ms: Process {process.get_pid()} arrived; added to ready queue {queue}")
    return t


def dispatch_process(process, active, queue, data, t_cs):
    """
    Dispatch a process from the ready queue.
    Update its wait time and schedule its CPU burst.
    """
    # Update wait time.
    if process.get_type():
        data.cpu_total_wait += process.get_sort_time() - process.get_ready_time()
    else:
        data.io_total_wait += process.get_sort_time() - process.get_ready_time()

    # Dispatch: Add half the context switch time before running.
    t = process.get_sort_time() + t_cs // 2
    active = process
    process.set_state("running")
    burst_duration = process.get_bursts()[0][0]
    process.set_sort_time(process.get_sort_time() + burst_duration + t_cs // 2)
    queue.add(process)

    if process.get_type():
        data.cpu_context_switches += 1
        data.cpu_total_bursts += 1
    else:
        data.io_context_switches += 1
        data.io_total_bursts += 1

    if t < 10000:
        print(f"time {t}ms: Process {process.get_pid()} started using the CPU for {burst_duration}ms burst {queue}")
    return t, active


def handle_running(process, queue, data, t, t_cs):
    """
    Handle a running process:
      - Add its CPU burst duration to the CPU busy time.
      - If it's the last burst, terminate it.
      - Otherwise, update its sort time for the I/O burst and set it to waiting.
    Returns updated time, active process (None after switching out), and a flag if terminated.
    """
    burst_duration = process.get_bursts()[0][0]
    data.cpu_busy += burst_duration
    t = process.get_sort_time()

    if len(process.get_bursts()) == 1:
        process.set_state("terminated")
        print(f"time {t}ms: Process {process.get_pid()} terminated {queue}")
        active = None
        t += t_cs // 2
        if process.get_type():
            data.cpu_total_turnaround += t - process.get_ready_time()
            data.cpu_total_bursts += 1
        else:
            data.io_total_turnaround += t - process.get_ready_time()
            data.io_total_bursts += 1
        return t, None, True
    else:
        t += t_cs // 2
        # Schedule I/O: Add the I/O burst time plus half context switch time.
        process.set_sort_time(process.get_sort_time() + process.get_bursts()[0][1] + t_cs // 2)
        process.remove_burst()
        process.set_state("waiting")
        if process.get_type():
            data.cpu_total_turnaround += t - process.get_ready_time()
        else:
            data.io_total_turnaround += t - process.get_ready_time()
        queue.add(process)
        if t < 10000:
            print(f"time {t}ms: Process {process.get_pid()} completed a CPU burst; {len(process.get_bursts())} bursts to go {queue}")
            print(f"time {t}ms: Process {process.get_pid()} switching out of CPU; blocking on I/O until time {process.get_sort_time()}ms {queue}")
        active = None
        return t, active, False


def handle_waiting(process, queue, t_cs, active):
    """Handle a process that has completed I/O and is ready to run again."""
    t = process.get_sort_time()
    process.set_ready_time(t)
    process = set_ready(process, active, t_cs)
    queue.add(process)
    if t < 10000:
        print(f"time {t}ms: Process {process.get_pid()} completed I/O; added to ready queue {queue}")
    return t


def handle_ready_with_active(process, active, queue, t_cs):
    """If a process is ready while another is active, adjust its sort time."""
    process.set_sort_time(active.get_sort_time() + t_cs // 2)
    queue.add(process)


def set_ready(process, active, t_cs):
    """
    Set a process's state to 'ready'.
    If there's an active process, its sort time is adjusted by half the context switch time.
    """
    process.set_state("ready")
    if active:
        process.set_sort_time(active.get_sort_time() + t_cs // 2)
    return process
