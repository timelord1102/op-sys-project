import math


'''
TODO: wait times and turnaround times for each process
'''

class Process:

    def __init__(self, pid, arrival_time, bursts, process_type, alpha, tau):
        self.pid = pid
        self.arrival_time = arrival_time
        self.bursts = bursts
        self.type = "CPU-bound" if process_type else "IO-bound"
        self.tau = tau
        self.alpha=alpha
        self.old_tau = -1
        self.wait_times = []
        self.turnaround_times = []
        self.start_wait = -1

    def get_pid(self):
        return self.pid

    def get_arrival_time(self):
        return self.arrival_time

    def get_bursts(self):
        return self.bursts

    def get_type(self):
        return self.type

    def begin_wait(self,t):
        # print(f"beginning wait for {self.pid} at time {t}")
        self.start_wait = t

    def end_wait(self,t):
        # print(f"ending wait for {self.pid} at {t}")
        self.wait_times.append(t-self.start_wait)

    def compute_turnaround(self,t):
        # print(f"computed turnaround for {self.pid}: {t-self.start_wait}ms")
        self.turnaround_times.append(t-self.start_wait)

    def get_turnaround(self):
        return self.turnaround_times

    def get_wait(self):
        return self.wait_times

    def recalculate_tau(self):
        tau_new = self.alpha*self.bursts[0][0] + (1-self.alpha)*self.tau
        self.old_tau = self.tau
        self.tau = math.ceil(tau_new)

    def get_tau(self):
        return self.tau

    def get_old_tau(self):
        return self.old_tau

    def complete_burst(self):
        self.bursts.pop(0)

    def __lt__(self,other):
        if self.tau != other.tau:
            return self.tau < other.tau
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
