from event import Event
import heapq
import math

class SRT:
    def __init__(self, processes, t_cs):
        self.processes = processes
        self.t_cs = t_cs
        self.event_queue = []   # min-heap for events
        self.ready_queue = []   # min-heap for processes waiting to run (ordered by tau)
        self.active = None      # currently running process
        self.termination = 0
        # You can add additional statistics here (e.g., total CPU busy time, etc.)

    def to_str_ready(self):
        return "[ " + " ".join(p.get_pid() for p in self.ready_queue) + " ]"

    def schedule(self):
        # Initialize event queue with all arrival events.
        self.event_queue = [Event(p.get_arrival_time(), "arrival", p, self.t_cs)
                            for p in self.processes]
        heapq.heapify(self.event_queue)
        t = 0

        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            t = event.get_t()
            self.execute_event(event, t)

        print(f"time {t}ms: Simulator ended for SRT [Q empty]")
        self.compute_simout()

    def execute_event(self, event, t):
        # For events before 10000ms, print details.
        print_event = t < 10000
        if event.type == "arrival":
            self.handle_arrival(event, t)
        elif event.type == "switch_in":
            self.handle_switch_in(event, t)
        elif event.type == "cpu_start":
            self.handle_cpu_start(event, t)
        elif event.type == "cpu_end":
            self.handle_cpu_end(event, t)
        elif event.type == "preempt":
            self.handle_preempt(event, t)
        elif event.type == "io_block":
            self.handle_io_block(event, t)
        elif event.type == "io_end":
            self.handle_io_end(event, t)
        elif event.type == "tau_recalc":
            self.handle_tau_recalc(event, t)
        elif event.type == "terminate":
            self.handle_terminate(event, t)

    def handle_arrival(self, event, t):
        p = event.get_process()
        p.begin_wait(t)
        heapq.heappush(self.ready_queue, p)
        print(f"time {t}ms: Process {p.get_pid()} (tau {p.get_tau()}ms) arrived; added to ready queue {self.to_str_ready()}")
        # If no process is active, dispatch the process.
        if self.active is None:
            heapq.heappush(self.event_queue, Event(t, "switch_in", p, self.t_cs))
        else:
            # Preemption check: if new process has lower tau than active's remaining burst.
            remaining = self.active.get_bursts()[0][0] - (t - self.active.run_start)
            if p.get_tau() < remaining:
                heapq.heappush(self.event_queue, Event(t, "preempt", self.active, self.t_cs))

    def handle_switch_in(self, event, t):
        if self.active is None and self.ready_queue:
            p = heapq.heappop(self.ready_queue)
            p.end_wait(t)
            self.active = p
            # Schedule cpu_start after half context-switch delay.
            heapq.heappush(self.event_queue, Event(t + int(self.t_cs/2), "cpu_start", p, self.t_cs))
            print(f"time {t}ms: Process {p.get_pid()} switching in; ready queue: {self.to_str_ready()}")

    def handle_cpu_start(self, event, t):
        p = event.get_process()
        p.run_start = t
        burst = p.get_bursts()[0][0]
        print(f"time {t}ms: Process {p.get_pid()} started CPU burst for {burst}ms")
        # Schedule CPU end.
        heapq.heappush(self.event_queue, Event(t + burst, "cpu_end", p, self.t_cs))

    def handle_cpu_end(self, event, t):
        p = event.get_process()
        # Complete turnaround: use end-of-burst time plus a half context-switch delay.
        p.compute_turnaround(t + int(self.t_cs/2))
        if len(p.get_bursts()) == 1:
            # Last burst completed: terminate.
            p.complete_burst()
            p.set_state("terminated")
            print(f"time {t}ms: Process {p.get_pid()} terminated")
            self.active = None
            # Dispatch next process if available.
            if self.ready_queue:
                heapq.heappush(self.event_queue, Event(t + int(self.t_cs/2), "switch_in", self.ready_queue[0], self.t_cs))
            else:
                # If no ready process remains, and event queue is nearly empty, schedule terminate.
                if not self.event_queue:
                    heapq.heappush(self.event_queue, Event(t + int(self.t_cs/2), "terminate", None, self.t_cs))
        else:
            # Burst complete but more bursts remain.
            print(f"time {t}ms: Process {p.get_pid()} completed CPU burst; scheduling I/O")
            # For SRT, we immediately recalculate tau.
            heapq.heappush(self.event_queue, Event(t, "tau_recalc", p, self.t_cs))
            # Schedule I/O block event.
            heapq.heappush(self.event_queue, Event(t, "io_block", p, self.t_cs))
            self.active = None
            if self.ready_queue:
                heapq.heappush(self.event_queue, Event(t + int(self.t_cs/2), "switch_in", self.ready_queue[0], self.t_cs))

    def handle_preempt(self, event, t):
        p = event.get_process()
        executed = t - p.run_start
        remaining = p.get_bursts()[0][0] - executed
        p.get_bursts()[0][0] = remaining
        p.begin_wait(t)
        heapq.heappush(self.ready_queue, p)
        print(f"time {t}ms: Process {p.get_pid()} preempted with remaining burst {remaining}ms; ready queue: {self.to_str_ready()}")
        self.active = None
        if self.ready_queue:
            next_p = heapq.heappop(self.ready_queue)
            next_p.end_wait(t)
            self.active = next_p
            heapq.heappush(self.event_queue, Event(t + int(self.t_cs/2), "cpu_start", next_p, self.t_cs))

    def handle_io_block(self, event, t):
        p = event.get_process()
        print(f"time {t}ms: Process {p.get_pid()} blocking for I/O")
        io_time = p.get_bursts()[0][1]
        # Schedule io_end after I/O burst plus a half context-switch delay.
        heapq.heappush(self.event_queue, Event(t + io_time + int(self.t_cs/2), "io_end", p, self.t_cs))

    def handle_io_end(self, event, t):
        p = event.get_process()
        p.complete_burst()
        p.begin_wait(t)
        heapq.heappush(self.ready_queue, p)
        print(f"time {t}ms: Process {p.get_pid()} completed I/O; added to ready queue {self.to_str_ready()}")
        if self.active is None:
            heapq.heappush(self.event_queue, Event(t, "switch_in", p, self.t_cs))

    def handle_tau_recalc(self, event, t):
        p = event.get_process()
        old = p.get_tau()
        p.recalculate_tau()
        print(f"time {t}ms: Process {p.get_pid()} tau recalculated: old tau {old}ms => new tau {p.get_tau()}ms")

    def handle_terminate(self, event, t):
        print(f"time {t}ms: Simulator terminated")
        self.compute_simout()

    def compute_simout(self):
        # Compute and output simulation statistics.
        pass
