import bisect

class ReadyQueue:
    def __init__(self, queue_type):
        self.queue = []
        self.queue_type = queue_type

    def add(self, process):
        self.queue.append(process)
        self.queue = sorted(self.queue, key=lambda x: x.get_sort_time())

    def pop(self):
        return self.queue.pop(0)

    def get(self, i):
        if i >= len(self.queue):
            return None
        return self.queue[i]

    def remove(self, process):
        self.queue.remove(process)

    def size(self):
        return len(self.queue)

    def __str__(self):
        temp_queue = self.queue.copy()
        if self.queue_type == "SJF":
            temp_queue = sorted(temp_queue, key=lambda x: x.get_tau())
        s = '[Q '

        for process in temp_queue:
            if process.get_state() == "ready":
                s += process.get_pid() + " "

        if len(s) == 3:
            s += "empty]"

        s = s[:-1] + ']'
        return s
