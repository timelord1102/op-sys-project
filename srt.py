import algorithmdata as ad
import ready_queue as rq

def srt(processes, t_cs):
    data = ad.AlgorithmData("SRT")
    queue = rq.ReadyQueue("SRT")

    lowest_tau = None

    for process in processes:
        queue.add(process)

    active = None
    t = 0
    print(f"time {t}ms: Simulator started for SRT {queue}")

    while queue.size() > 0:
        process = queue.pop()

        # Handle process arrival.
        if process.get_state() == "None":
            t, lowest_tau = handle_arrival(process, active, queue, data, t_cs, lowest_tau)

        # Dispatch a ready process if no process is active.
        elif active is None and lowest_tau is not None and process == lowest_tau:
            t, active, _ = dispatch_process(process, active, queue, data, t_cs)

        # Process is running; handle CPU burst completion.
        elif process.get_state() == "running":
            t, active, terminated, lowest_tau = handle_running(process, queue, data, t, t_cs, lowest_tau)
            if terminated:
                continue  # Process terminated; go to next iteration.

        # Process has been waiting (finishing I/O); update its state.
        elif process.get_state() == "waiting":
            t, lowest_tau = handle_waiting(process, queue, t_cs, active)

        # If process is ready but another is active, update its sort time.
        elif process.get_state() == "ready" and active:
            handle_ready_with_active(process, active, queue, t_cs)

        elif process.get_state() == "ready":
            process, lowest_tau = set_ready(process, active, t_cs, lowest_tau)
            queue.add(process)

    print(f"time {t}ms: Simulator ended for SRT {queue}")
    data.total_run_time = t
    print(data)

def handle_arrival(process, active, queue, data, t_cs, lowest_tau):
    """Handle a process that is just arriving in the system."""
    process, lowest_tau = set_ready(process, active, t_cs, lowest_tau)
    t = process.get_arrival_time()
    queue.add(process)
    if process.get_type():
        data.num_cpu_processes += 1
    else:
        data.num_io_processes += 1
    if t < 10000:
        print(f"time {t}ms: Process {process.get_pid()} (tau {process.get_tau()}ms) arrived; added to ready queue {queue}")
    return t, lowest_tau

def dispatch_process(process, active, queue, data, t_cs):
    if active:
        active.set_state("ready")
        active.bursts[0][0] -= active.run_start
        active.set_ready_time(process.get_sort_time())
        active.set_sort_time(process.get_sort_time())
        queue.add(active)
    process.set_state("running")
    process.run_start = process.get_sort_time()
    process.set_sort_time(process.get_sort_time())
    t = process.get_sort_time() + t_cs/2
    print(f"time {t}ms: Process {process.get_pid()} (tau {process.get_tau()}ms) started using the CPU for {process.get_bursts()[0][0]}ms burst")
    active = process  # <-- FIX: update active process here.
    return t, process, active

def handle_running(process, queue, data, t, t_cs, lowest_tau):
    process.remove_burst()
    if len(process.get_bursts()) == 0:
        t = process.get_sort_time()
        process.set_state("terminated")
        print(f"time {t}ms: Process {process.get_pid()} terminated")
        data.cpu_total_turnaround += t - process.get_arrival_time()
        data.cpu_total_burst += t - process.get_arrival_time()
        data.cpu_total_wait += t - process.get_arrival_time() - data.cpu_total_burst
        return t, None, True, lowest_tau
    else:
        t = process.get_sort_time()
        process.set_state("waiting")
        print(f"time {t}ms: Process {process.get_pid()} (tau {process.get_tau()}ms) completed a CPU burst; {len(process.get_bursts())} burst{'s' if len(process.get_bursts()) != 1 else ''} to go")
        return t, None, False, lowest_tau

def handle_waiting(process, queue, t_cs, active):
    if active:
        active.set_state("ready")
        active.bursts[0][0] -= active.run_start
        active.set_ready_time(process.get_sort_time())
        active.set_sort_time(process.get_sort_time())
        queue.add(active)
    process.set_state("ready")
    process.set_sort_time(process.get_sort_time())
    print(f"time {process.get_sort_time()}ms: Process {process.get_pid()} switching out of CPU; blocking on I/O until time {process.get_sort_time() + process.get_bursts()[0][1] + t_cs/2}ms")
    return process.get_sort_time(), process

def handle_ready_with_active(process, active, queue, t_cs):
    if process.get_sort_time() < active.get_sort_time():
        process.set_sort_time(active.get_sort_time())
        print(f"time {process.get_sort_time()}ms: Process {process.get_pid()} (tau {process.get_tau()}ms) will preempt {active.get_pid()} {queue}")
    else:
        print(f"time {process.get_sort_time()}ms: Process {process.get_pid()} (tau {process.get_tau()}ms) arrived; added to ready queue {queue}")

def set_ready(process, active, t_cs, lowest_tau):
    if lowest_tau is None or lowest_tau.get_tau() > process.get_tau():
        lowest_tau = process
    if active is not None and lowest_tau.get_tau() < active.get_tau():
        # Removed dispatch call here to avoid premature dispatch.
        process.set_state("ready")
        process.set_sort_time(process.get_arrival_time())
    else:
        process.set_state("ready")
        process.set_sort_time(process.get_arrival_time())
    return process, lowest_tau
