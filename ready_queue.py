class ReadyQueue:
    def __init__(self, queue_type):
        self.queue = []
        self.queue_type = queue_type


    def add(self, process):
        self.queue.append(process)
        if self.queue_type == "SJF" or self.queue_type == "SRT":
            self.queue = sorted(self.queue, key=lambda x: x.get_tau())
        if self.queue_type == "FCFS":
            self.queue = sorted(self.queue, key=lambda x: x.get_sort_time())

    def pop(self):
        return self.queue.pop(0)

    def get(self, i):
        if i >= len(self.queue):
            return None
        return self.queue[i]

    def size(self):
        return len(self.queue)


    def __str__(self):
        s = '[Q '

        for process in self.queue:
            if process.get_state() == "ready":
                s += process.get_pid() + " "

        if len(s) == 3:
            s += "empty]"

        s = s[:-1] + ']'
        return s
