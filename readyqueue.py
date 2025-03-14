from event import Event
import heapq

class ReadyQueue:


    def __init__(self, processes, t_cs):
        if len(processes) == 0:
            print("empty queue")
        self.processes=processes
        self.ready_queue = []
        self.sjf_queue = []
        self.io_state = None
        self.active = None
        self.event_queue=[]
        self.t_cs = t_cs
        self.termination = 0

        self.burst_time = 0
        for p in processes: self.burst_time += sum(b[0] for b in p.get_bursts())
        self.cpu_context = 0
        self.io_context = 0
    
    def get_queue(self):
        return self.ready_queue
    
    def preempt(self):
        pass
# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               FCFS
# --------------------------------------------------------------------------------------------------------------------------------------
    # switch in happens at t but stalls t_cs/2 ms before beginning cpu_start
    def handle_switch_in_fcfs(self,event,print_event):
        if len(self.ready_queue) > 0 and not self.active:
            self.ready_queue[0].end_wait(event.get_t())

            if event.get_process().get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1
            p = self.ready_queue[0]
            self.active = p
            self.ready_queue.pop(0)
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    # switch out is reflected at the end of t+t_cs/2
    def handle_switch_out_fcfs(self,event,print_event):
        if len(event.get_process().get_bursts())-1 > 0:
            heapq.heappush(self.ready_queue,event.get_process())
        self.active=None

    # same as a switchout except don't add to the ready queue
    def io_active_switchout_fcfs(self,event,print_event):
        self.active=None

    def handle_io_switch_out_fcfs(self,event,print_event):
        self.io_state = self.active
        heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_out_io", self.active, self.t_cs))
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_in", self.ready_queue[0], self.t_cs))

    def fcfs(self):
        print(f"time 0ms: Simulator started for FCFS {self.to_str_fcfs()}")
        self.event_queue = [Event(p.get_arrival_time(), "arrival", p, self.t_cs) for p in self.processes]
        heapq.heapify(self.event_queue)

        # execute events as they arrive
        while (len(self.event_queue)>0):
            self.execute_event_fcfs(heapq.heappop(self.event_queue))

    def execute_event_fcfs(self, event):
        print_event = event.get_t() < 10000
        if event.type == "arrival":
            self.handle_arrival_fcfs(event,print_event)
        elif event.type == "switch_in":
            self.handle_switch_in_fcfs(event,print_event)
        elif event.type == "switch_out":
            self.handle_switch_out_fcfs(event,print_event)
        elif event.type == "io_switch":
            self.handle_io_switch_out_fcfs(event,print_event)
        elif event.type == "switch_out_io":
            self.io_active_switchout_fcfs(event,print_event)
        elif event.type == "cpu_start":
            self.handle_cpu_start_fcfs(event,print_event)
        elif event.type == "cpu_end": 
            self.handle_cpu_end_fcfs(event,print_event)
        elif event.type == "io_block":
            self.handle_io_block_fcfs(event,print_event)
        elif event.type == "io_end":
            self.handle_io_end_fcfs(event,print_event)
        elif event.type == "terminate":
            print(f"time {event.get_t()}ms: Simulator ended for FCFS [Q empty]")
            self.termination = event.get_t()
            self.compute_simout()

    def handle_arrival_fcfs(self,event,print_event):
        self.ready_queue.append(event.get_process())
        event.get_process().begin_wait(event.get_t())
        print(f"{event} {self.to_str_fcfs()}")
        if not self.active:
            # add it to the active state in t_cs/2 ms, but remove from ready queue immediately
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in",event.get_process(),self.t_cs))
    
    def handle_cpu_start_fcfs(self,event,print_event):
        print(f"{event} {self.to_str_fcfs()}")
        heapq.heappush(self.event_queue,Event(event.get_t()+self.active.get_bursts()[0][0],"cpu_end",self.active, self.t_cs))

    # cpu end: queue io event, switch out, switch in, queue new cpu start
    def handle_cpu_end_fcfs(self,event,print_event):
        event.get_process().compute_turnaround(event.get_t()+int(self.t_cs/2))

        # process has more cpu bursts to complete
        if len(event.process.get_bursts())-1 > 0:
            print(f"{event} {self.to_str_fcfs()}")
            heapq.heappush(self.event_queue,Event(event.get_t(), "io_block", self.active, self.t_cs))
            return
        # process is done, switching to next
        print(f"{event} {self.to_str_fcfs()}")
        # switch out actually happens at t+t_cs/2, switch in happens at t+t_cs/2 but waits t_cs/2 for cpu_start
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", self.active, self.t_cs))
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.ready_queue[0], self.t_cs))
        elif len(self.ready_queue) == 0 and len(self.event_queue) == 1: # only the switch out remains on the queue
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2),"terminate",None,self.t_cs))

    def handle_io_block_fcfs(self,event,print_event):
        print(f"{event} {self.to_str_fcfs()}")
        p = event.get_process()
        heapq.heappush(self.event_queue, Event(event.get_t(),"io_switch",p,self.t_cs))
        heapq.heappush(self.event_queue, Event(event.get_t()+p.get_bursts()[0][1]+int(self.t_cs/2), "io_end", p, self.t_cs))

    #  io completes -> add to queue -> check empty space
    def handle_io_end_fcfs(self,event,print_event):
        event.get_process().complete_burst()
        event.get_process().begin_wait(event.get_t())
        self.ready_queue.append(event.get_process())
        print(f"{event} {self.to_str_fcfs()}")
        self.io_state = None
        # attempt to switch in if nothing is already trying to switch in 
        if not self.active and len(self.ready_queue) == 1:
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in", self.ready_queue[0], self.t_cs))

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               SJF
# --------------------------------------------------------------------------------------------------------------------------------------

    # switch in happens at t but stalls t_cs/2 ms before beginning cpu_start
    def handle_switch_in_sjf(self,event,print_event):
        if len(self.sjf_queue) > 0 and not self.active:
            self.sjf_queue[0].end_wait(event.get_t())

            if event.get_process().get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1
            p = self.sjf_queue[0]
            self.active = p
            heapq.heappop(self.sjf_queue)
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    # switch out is reflected at the end of t+t_cs/2
    def handle_switch_out_sjf(self,event,print_event):
        if len(event.get_process().get_bursts())-1 > 0:
            heapq.heappush(self.sjf_queue,event.get_process())
        self.active=None

    def handle_io_switch_out_sjf(self,event,print_event):
        self.io_state = self.active
        heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_out_io", self.active, self.t_cs))

        if len(self.sjf_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_in", self.sjf_queue[0], self.t_cs))
    
    def io_active_switchout_sjf(self,event,print_event):
        self.active=None

    def sjf(self):
        print(f"time 0ms: Simulator started for SJF {self.to_str_sjf()}")
        self.event_queue = [Event(p.get_arrival_time(), "arrival", p, self.t_cs) for p in self.processes]
        heapq.heapify(self.event_queue)

        # execute events as they arrive
        while (len(self.event_queue)>0):
            self.execute_event_sjf(heapq.heappop(self.event_queue))

    def execute_event_sjf(self, event):
        print_event = event.get_t() < 10000
        if event.type == "arrival":
            self.handle_arrival_sjf(event,print_event)
        elif event.type == "switch_in":
            self.handle_switch_in_sjf(event,print_event)
        elif event.type == "switch_out":
            self.handle_switch_out_sjf(event,print_event)
        elif event.type == "switch_out_io":
            self.io_active_switchout_sjf(event,print_event)
        elif event.type == "io_switch":
            self.handle_io_switch_out_sjf(event,print_event)
        elif event.type == "cpu_start":
            self.handle_cpu_start_sjf(event,print_event)
        elif event.type == "cpu_end": 
            self.handle_cpu_end_sjf(event,print_event)
        elif event.type == "io_block":
            self.handle_io_block_sjf(event,print_event)
        elif event.type == "io_end":
            self.handle_io_end_sjf(event,print_event)
        elif event.type == "tau_recalc":
            self.handle_tau_recalc(event,print_event)
        elif event.type == "terminate":
            print(f"time {event.get_t()}ms: Simulator ended for SJF [Q empty]")
            self.termination = event.get_t()
            self.compute_simout()

    ''' each time a process gets added to the ready queue, we have to insert in tau-order '''
    def handle_arrival_sjf(self,event,print_event):
        heapq.heappush(self.sjf_queue, event.get_process())
        event.get_process().begin_wait(event.get_t())
        print(f"{event} {self.to_str_sjf()}")

        if not self.active:
            # add it to the active state in t_cs/2 ms, but remove from ready queue immediately
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in",event.get_process(),self.t_cs))
    
    def handle_cpu_start_sjf(self,event,print_event):
        print(f"{event} {self.to_str_sjf()}")
        heapq.heappush(self.event_queue,Event(event.get_t()+self.active.get_bursts()[0][0],"cpu_end",self.active, self.t_cs))

    # cpu end: queue io event, switch out, switch in, queue new cpu start
    def handle_cpu_end_sjf(self,event,print_event):
        event.get_process().compute_turnaround(event.get_t()+int(self.t_cs/2))
        # process has more cpu bursts to complete
        if len(event.process.get_bursts())-1 > 0:
            print(f"{event} {self.to_str_sjf()}")
            heapq.heappush(self.event_queue,Event(event.get_t(), "tau_recalc", self.active, self.t_cs))
            heapq.heappush(self.event_queue,Event(event.get_t(), "io_block", self.active, self.t_cs))
            return
        print(f"{event} {self.to_str_sjf()}")
        # switch out actually happens at t+t_cs/2, switch in happens at t+t_cs/2 but waits t_cs/2 for cpu_start
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", self.active, self.t_cs))
        if len(self.sjf_queue) > 0:
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.sjf_queue[0], self.t_cs))
        elif len(self.ready_queue) == 0 and len(self.event_queue) == 1: # only the switch out remains on the queue
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2),"terminate",None,self.t_cs))

    def handle_io_block_sjf(self,event,print_event):
        print(f"{event} {self.to_str_sjf()}")
        p = event.get_process()
        heapq.heappush(self.event_queue, Event(event.get_t(),"io_switch",p,self.t_cs))
        heapq.heappush(self.event_queue, Event(event.get_t()+p.get_bursts()[0][1]+int(self.t_cs/2), "io_end", p, self.t_cs))

    #  io completes -> add to queue -> check empty space
    def handle_io_end_sjf(self,event,print_event):
        event.get_process().complete_burst()
        event.get_process().begin_wait(event.get_t())
        heapq.heappush(self.sjf_queue, event.get_process())
        print(f"{event} {self.to_str_sjf()}")
        self.io_state = None
        if not self.active and len(self.sjf_queue) == 1:
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in", self.sjf_queue[0], self.t_cs))

    def handle_tau_recalc(self, event, print_event):
        self.active.recalculate_tau()
        print(f"{event} {self.to_str_sjf()}")

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               SRT
# --------------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               RR
# --------------------------------------------------------------------------------------------------------------------------------------

    def compute_simout(self):
        overall_avg = total_bursts = io_bursts = io_wait = cpu_bursts = cpu_wait = 0
        turnaround_avg = io_turnaround = cpu_turnaround = 0
        for p in self.processes:
            overall_avg += sum(p.get_wait())
            turnaround_avg += sum(p.get_turnaround())
            total_bursts += len(p.get_wait())
            if p.get_type() == "CPU-bound":
                cpu_bursts += len(p.get_wait())
                cpu_turnaround += sum(p.get_turnaround())
                cpu_wait += sum(p.get_wait())
            else:
                io_bursts += len(p.get_wait())
                io_turnaround += sum(p.get_turnaround())
                io_wait += sum(p.get_wait())
        
        if total_bursts == 0: total_bursts = 1
        if cpu_bursts == 0: cpu_bursts = 1
        if io_bursts == 0: io_bursts = 1
        cpu_utilization = self.burst_time / self.termination
        overall_avg /= total_bursts
        cpu_wait /= cpu_bursts
        io_wait /= io_bursts 
        turnaround_avg /= total_bursts
        cpu_turnaround /= cpu_bursts
        io_turnaround /= io_bursts
        
        print(f"cpu utilization: {cpu_utilization}")
        print(f"cpu wait: {cpu_wait}")
        print(f"io wait: {io_wait}")
        print(f"overall wait: {overall_avg}")
        print(f"cpu turnaround: {cpu_turnaround}")
        print(f"io turnaround: {io_turnaround}")
        print(f"overall turnaround: {turnaround_avg}")
        print(f"cpu context switches: {self.cpu_context}")
        print(f"io context switches: {self.io_context}")
        print(f"all context switches: {self.cpu_context + self.io_context}")

    # printing for fcfs
    def to_str_fcfs(self):
        if len(self.ready_queue) == 0:
            return "[Q empty]"
        q = "[Q" 
        for p in self.ready_queue:
            q += ' '+p.get_pid()
        q += "]"
        return q

    def to_str_sjf(self):
        if len(self.sjf_queue) == 0:
            return "[Q empty]"
        q = "[Q" 
        for p in heapq.nsmallest(len(self.sjf_queue), self.sjf_queue):
            q += ' '+p.get_pid()
        q += "]"
        return q