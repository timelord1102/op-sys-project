class Event:

    def __init__(self, t, type, process, t_cs):
        self.t = t
        self.type=type
        self.process = process
        self.t_cs = t_cs
        self.priority=1000
        if type == "arrival":
            self.priority=3
        elif type == "cpu_start":
            self.priority=1
        elif type == "cpu_end":
            self.priority=0
        elif type == "switch_out" or type == "switch_out_io":
            self.priority = -1
        elif type == "switch_in":
            self.priority = 100
        elif type == "io_end":
            self.priority=2

    def get_t(self):
        return self.t

    def get_process(self):
        return self.process

    # edit to account for other ties
    def __lt__(self,other):
        if self.t != other.get_t():
            return self.t < other.get_t()
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.process.get_pid() < other.process.get_pid()

    ''' TODO: string functions for each algo (some need tau, others don't)'''
#     def __str__(self):
#         if self.type == "arrival":
#             return f"time {self.t}ms: Process {self.process.get_pid()} arrived; added to ready queue"
#         elif self.type == "cpu_start":
#             return f"time {self.t}ms: Process {self.process.get_pid()} started using the CPU for {self.process.get_bursts()[0][0]}ms burst"
#         elif self.type == "cpu_end":
#             if len(self.process.get_bursts())-1 == 0:
#                 return f"time {self.t}ms: Process {self.process.get_pid()} terminated"
#             elif len(self.process.get_bursts())-1 == 1:
#                 return f"time {self.t}ms: Process {self.process.get_pid()} completed a CPU burst; 1 burst to go"
#             return f"time {self.t}ms: Process {self.process.get_pid()} completed a CPU burst; {len(self.process.get_bursts())-1} bursts to go"
#         elif self.type == "io_block":
#             return f"time {self.t}ms: Process {self.process.get_pid()} switching out of CPU; blocking on I/O until time \
# {self.t+self.process.get_bursts()[0][1]+int(self.t_cs/2)}ms"
#         elif self.type == "io_end":
#             return f"time {self.t}ms: Process {self.process.get_pid()} completed I/O; added to ready queue"
#         else:
#             return f"t: {self.t}, type: {self.type}, pid: {self.process.get_pid()}"

    def __str__(self):
        if self.type == "arrival":
            return f"time {self.t}ms: Process {self.process.get_pid()} (tau {self.process.get_tau()}ms) arrived; added to ready queue"
        elif self.type == "cpu_start":
            return f"time {self.t}ms: Process {self.process.get_pid()} (tau {self.process.get_tau()}ms) started using the CPU for {self.process.get_bursts()[0][0]}ms burst"
        elif self.type == "cpu_end":
            if len(self.process.get_bursts())-1 == 0:
                return f"time {self.t}ms: Process {self.process.get_pid()} terminated"
            elif len(self.process.get_bursts())-1 == 1:
                return f"time {self.t}ms: Process {self.process.get_pid()} (tau {self.process.get_tau()}ms) completed a CPU burst; {len(self.process.get_bursts())-1} burst to go"
            return f"time {self.t}ms: Process {self.process.get_pid()} (tau {self.process.get_tau()}ms) completed a CPU burst; {len(self.process.get_bursts())-1} bursts to go"
        elif self.type == "io_block":
            return f"time {self.t}ms: Process {self.process.get_pid()} switching out of CPU; blocking on I/O until time \
{self.t+self.process.get_bursts()[0][1]+int(self.t_cs/2)}ms"
        elif self.type == "io_end":
            return f"time {self.t}ms: Process {self.process.get_pid()} (tau {self.process.get_tau()}ms) completed I/O; added to ready queue"
        elif self.type == "tau_recalc":
            return f"time {self.t}ms: Recalculated tau for process {self.process.get_pid()}: old tau {self.process.get_old_tau()}ms ==> \
new tau {self.process.get_tau()}ms"
        elif self.type == "preempt":
            return f"time {self.t}ms: Process {self.process.get_pid()} (tau {self.process.get_tau()}ms) preempted )"
        else:
            return f"t: {self.t}, type: {self.type}, pid: {self.process.get_pid()}"
