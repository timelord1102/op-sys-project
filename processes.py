class Process:
    def __init__(self, pid, arrival_time, bursts, process_type, alpha, tau):
        self.state = "None"
        self.pid = pid
        self.arrival_time = arrival_time
        self.bursts = bursts
        self.type = process_type
        self.tau = tau
        self.alpha=alpha
        self.sort_time = arrival_time
        self.ready_time = arrival_time


    def get_pid(self):
        return self.pid

    def get_arrival_time(self):
        return self.arrival_time

    def remaining_bursts(self):
        return len(self.bursts)

    def get_bursts(self):
        return self.bursts

    def remove_burst(self):
        self.bursts = self.bursts[1:]

    def get_type(self):
        return self.type

    def get_tau(self):
        return self.tau

    def get_alpha(self):
        return self.alpha

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def get_sort_time(self):
        return self.sort_time

    def set_sort_time(self, time):
        self.sort_time = time

    def get_ready_time(self):
        return self.ready_time

    def set_ready_time(self, time):
        self.ready_time = time
