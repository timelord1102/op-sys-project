class Event:

    '''
    Event class: each object corresponds to an event that the scheduler will execute
    :param: t (int): timestamp for when event should be executed
    :param: type (str): type of event (i.e, arrival, cpu_start, preempt)
    :param: process (Process): Process object associated with the event; if we need to preempt, we know which process to preempt, etc
    :param: t_cs (int): time required for a context switch, given from command line args in main
    :param: priority (int): priority an event should take place if there's a tie in time stamp. not sure if theyre all 100% correct
                            but there's supposed to be a specific order     
    '''

    def __init__(self, t, type, process, t_cs):
        self.t = t
        self.type=type
        self.process = process
        self.t_cs = t_cs
        self.priority=1000
        # active state must be vacated and ready queue adjusted as soon as possible
        if type == "switch_out" or type == "switch_out_io" or type == "io_switch":
            self.priority = -2        
        elif type == "preempt":
            self.priority = -1
        elif type == "cpu_end":
            self.priority=0
        elif type == "cpu_start":
            self.priority=1
        # tau prints must be between burst completion/io blocking
        elif type == "tau_recalc":
            self.priority = 2
        elif type == "io_block":
            self.priority = 3
        elif type == "io_end":
            self.priority=4
        elif type == "arrival":
            self.priority=5

    def get_t(self):
        return self.t
    
    def get_process(self):
        return self.process
    
    # less than operator, required for heapq to insert in order
    # sort by time first, then by priorty, then by pid of the process
    def __lt__(self,other):
        if self.t != other.get_t():
            return self.t < other.get_t()
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.process.get_pid() < other.process.get_pid()
        
    ''' TODO: string functions for each algo (some need tau, others don't)''' 
    def to_str(self):
        if self.type == "arrival":
            return f"time {self.t}ms: Process {self.process.get_pid()} arrived; added to ready queue"
        elif self.type == "cpu_start":
            if self.process.get_bursts()[0][0] != self.process.get_original_bursts()[0][0]:
                return f"time {self.t}ms: Process {self.process.get_pid()} started using the CPU for remaining \
{self.process.get_bursts()[0][0]}ms of {self.process.get_original_bursts()[0][0]}ms burst"
            else:
                return f"time {self.t}ms: Process {self.process.get_pid()} started using the CPU for {self.process.get_bursts()[0][0]}ms burst"
        elif self.type == "cpu_end":
            if len(self.process.get_bursts())-1 == 0:
                return f"time {self.t}ms: Process {self.process.get_pid()} terminated"
            elif len(self.process.get_bursts())-1 == 1:
                return f"time {self.t}ms: Process {self.process.get_pid()} completed a CPU burst; 1 burst to go"
            return f"time {self.t}ms: Process {self.process.get_pid()} completed a CPU burst; {len(self.process.get_bursts())-1} bursts to go"
        elif self.type == "io_block":
            return f"time {self.t}ms: Process {self.process.get_pid()} switching out of CPU; blocking on I/O until time \
{self.t+self.process.get_bursts()[0][1]+int(self.t_cs/2)}ms"
        elif self.type == "io_end":
            return f"time {self.t}ms: Process {self.process.get_pid()} completed I/O; added to ready queue"
        else:
            return f"t: {self.t}, type: {self.type}, pid: {self.process.get_pid()}"

    def to_str_tau(self):
        if (self.process.alpha == -1):
            return self.to_str()
        if self.type == "arrival":
            return f"time {self.t}ms: Process {self.process.get_pid()} (tau {self.process.get_tau()}ms) arrived; added to ready queue"
        elif self.type == "cpu_start":
            if self.process.get_bursts()[0][0] != self.process.get_original_bursts()[0][0]:
                return f"time {self.t}ms: Process {self.process.get_pid()} (tau {self.process.get_tau()}ms) started using the CPU for remaining \
{self.process.get_bursts()[0][0]}ms of {self.process.get_original_bursts()[0][0]}ms burst"
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
        else:
            return f"t: {self.t}, type: {self.type}, pid: {self.process.get_pid()}"