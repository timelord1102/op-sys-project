import math

class Process:

    '''
    Process class
    :param: pid (str): Process name, ie 'A0'
    :param: arrival_time (int): time that the process should first arrive in ready queue
    :param: bursts (list[int,int]): first index is cpu burst, second index is io burst. 
                                    ***the last burst consists only of [cpu_burst]***
    :param: type (str): type of process, either 'CPU-bound' or 'I/O-bound'
    :param: tau (int): tau value given by command line args
    '''

    def __init__(self, pid, arrival_time, bursts, process_type, alpha, tau):
        self.pid = pid
        self.arrival_time = arrival_time
        self.bursts = bursts
        self.original_bursts = bursts.copy()
        self.type = process_type
        self.tau = tau
        self.remaining_tau = tau
        self.alpha=alpha
        self.old_tau = -1
        # current_wait is the accumulator for one specific wait time
        self.current_wait = 0
        # wait_times list stores the wait time of each cpu burst
        self.wait_times = []
        # turnaround_times list stores the turnaround times of each cpu burst 
        self.turnaround_times = [] 
        # start_wait defines when a process enters the ready queue
        self.start_wait = -1
        # burst_arrival will be set when a new cpu burst begins execution
        self.burst_arrival = 0
        self.cpu_start = 0

    def get_pid(self):
        return self.pid
    
    def get_arrival_time(self):
        return self.arrival_time
    
    def get_bursts(self):
        return self.bursts

    def get_type(self):
        return self.type

    # use this function when a process enters the ready queue with a completely new cpu burst
    def set_burst_arrival(self, t):
        self.burst_arrival = t

    # use this function to start waiting, ie when a process enters the queue at any point
    def begin_wait(self,t):
        self.start_wait = t

    # add wait will be called when the process begins cpu execution. use this to actually accumulate 
    # the wait time of the cpu burst
    def add_wait(self, t):
        self.current_wait += t - self.start_wait 

    # turnaround time = completion - start time for a given burst
    def compute_turnaround(self,t):
        self.turnaround_times.append(t-self.burst_arrival)

    def get_turnaround(self):
        return self.turnaround_times

    def get_wait(self):
        return self.wait_times

    # the following two functions are used for predicted tau values
    def set_cpu_start(self,t):
        self.cpu_start = t

    def set_remaining_tau(self, tau):
        self.remaining_tau = tau
    
    def calc_remaining_tau(self,t):
        return self.remaining_tau - (t - self.cpu_start)

    def get_remaining_tau(self):
        return self.remaining_tau
    
    # this is just the formula we were given for tau+1
    def recalculate_tau(self):
        tau_new = self.alpha*self.original_bursts[0][0] + (1-self.alpha)*self.tau
        self.old_tau = self.tau
        self.tau = math.ceil(tau_new)
        self.remaining_tau = self.tau

    def get_tau(self):
        return self.tau
    
    def get_old_tau(self):
        return self.old_tau

    # this function is relevant for preemptions: when only part of the burst is completed, this function 
    # updates the remaining burst time in the process
    # i think this function can be one line ill fix it later
    def partial_burst(self, amount_completed):
        if len(self.bursts) == 1:
            self.bursts[0] = [self.bursts[0][0]-amount_completed]
        else:
            self.bursts[0] = [self.bursts[0][0]-amount_completed, self.bursts[0][1]]

    # this function is used when a cpu burst fully finishes, including the cpu and io burst. 
    # the pair is removed from the bursts list, and the accumulator for wait time is set to 0 for the next burst.
    def complete_burst(self):
        self.bursts.pop(0)
        self.original_bursts.pop(0)
        self.wait_times.append(self.current_wait)
        self.current_wait = 0

    def get_original_bursts(self):
        return self.original_bursts

    def __lt__(self,other):
        if self.remaining_tau != other.remaining_tau:
            return self.remaining_tau < other.remaining_tau
        return self.pid < other.pid

    def __str__(self):
        s=''
        if len(self.bursts) == 1:
            s = f"{self.type} process {self.pid}: arrival time {self.arrival_time}ms; {len(self.bursts)} CPU burst:\n"
        else:
            s = f"{self.type} process {self.pid}: arrival time {self.arrival_time}ms; {len(self.bursts)} CPU bursts:\n"
        for b in self.bursts:
            if (len(b)) > 1:
                s += f"==> CPU burst {b[0]}ms ==> I/O burst {b[1]}ms\n"
            else:
                s += f"==> CPU burst {b[0]}ms\n"
        s += f"tau: {self.tau}\n"
        return s