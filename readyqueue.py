from event import Event
import math
import heapq
import copy 

class ReadyQueue:

    '''
    ReadyQueue class
    active refers to the process in the active/running state
    io_state refers to the process in the io_state
    ready_queue is a basic list that will store processes. this will only be used in fcfs, rr
    sjf_queue is intended to be heapified with heapq to sort processes by tau value. this is useful for sjf, srt 
    (make a new variable for srt if you need)

    '''

    def __init__(self, processes, t_cs):
        self.processes=processes
        self.original_processes=copy.deepcopy(self.processes)
        self.ready_queue = []
        self.sjf_queue = []
        self.io_state = None
        self.active = None
        self.event_queue=[]
        self.t_cs = t_cs

        # everything under here is used for the statistics, worry about this once the algo works
        # termination is the time the algo completes 
        self.termination = 0
        self.t_slice=0
        self.burst_time = 0
        for p in processes: self.burst_time += sum(b[0] for b in p.get_bursts())
        self.cpu_context = 0
        self.io_context = 0
        self.cpu_preempt = 0
        self.io_preempt = 0
    
    def get_queue(self):
        return self.ready_queue
    
# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               FCFS
# --------------------------------------------------------------------------------------------------------------------------------------
    # switch the first process from the ready queue into the active state. only perform
    # this action if there's a process in the ready queue and nothing is already using the cpu.
    # switch ins happen immediately in terms of printing, but the process waits in the active state for 
    # t_cs/2ms - this is why we queue the cpu_start with the added time
    def handle_switch_in_fcfs(self,event,print_event):
        if len(self.ready_queue) > 0 and not self.active:
            self.ready_queue[0].add_wait(event.get_t())
            if self.ready_queue[0].get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1
            p = self.ready_queue[0]
            self.active = p
            self.ready_queue.pop(0)
            # queue a cpu_start at time t+t_cs/2. 
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    # switch out is reflected at the end of t+t_cs/2. we only add back to the ready queue if theres more than one 
    # burst remaining.
    def handle_switch_out_fcfs(self,event,print_event):
        if len(event.get_process().get_bursts()) > 0:
            self.ready_queue.append(event.get_process())
        self.active=None

    # same as a switchout except don't add to the ready queue
    # this function is used to switch out the active state at the desired time stamp
    def io_active_switchout_fcfs(self,event,print_event):
        self.active=None

    # io_switch_out is responsible for moving the active process to the io state.
    # switch_out_io is scheduled for t + t_cs/2 to account for the switchout, and 
    # we schedule a switch-in if there are processes in the ready queue.
    # switch-in happens at t+t_cs/2, and switch-in schedules cpu_start at t+t_cs/2 to account for a full context switch
    def handle_io_switch_out_fcfs(self,event,print_event):
        self.io_state = self.active
        heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_out_io", self.active, self.t_cs))
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_in", self.ready_queue[0], self.t_cs))

    # driver function, basically queue arrival events and then loop through the priority queue until done
    def fcfs(self):
        print(f"time 0ms: Simulator started for FCFS {self.to_str_fcfs()}")
        self.event_queue = [Event(p.get_arrival_time(), "arrival", p, self.t_cs) for p in self.processes]
        heapq.heapify(self.event_queue)

        # execute events as they arrive
        while (len(self.event_queue)>0):
            self.execute_event_fcfs(heapq.heappop(self.event_queue))

    def execute_event_fcfs(self, event):
        # print event isnt used yet, but we only need to print things before 10000ms (mostly)
        print_event = event.get_t() < 10000
        if event.type == "arrival":
            self.handle_arrival_fcfs(event,print_event)
        elif event.type == "switch_in":
            self.handle_switch_in_fcfs(event,print_event)
        elif event.type == "switch_out":
            self.handle_switch_out_fcfs(event,print_event)
        # bad naming but io_switch will call a switch_out_io (i can fix this at some point for clarity)
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

    # on arrival, add the process to the ready queue and switch in a new process if 
    # nothing is using the cpu currently.
    def handle_arrival_fcfs(self,event,print_event):
        self.ready_queue.append(event.get_process())
        
        # set the starting time for wait and turnaround times for this cpu burst
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())
        
        print(f"{event} {self.to_str_fcfs()}")
        if not self.active:
            # add to the active state in t_cs/2 ms, but remove from ready queue immediately
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in",event.get_process(),self.t_cs))
    
    # queue a cpu end for the active process. ** this assumes no preemptions **
    def handle_cpu_start_fcfs(self,event,print_event):
        print(f"{event} {self.to_str_fcfs()}")
        # self.active is a process, which stores bursts as [[cpu_burst,io_burst]...,[cpu_burst]]
        heapq.heappush(self.event_queue,Event(event.get_t()+self.active.get_bursts()[0][0],"cpu_end",self.active, self.t_cs))

    # cpu end: queue io event if if has one, otherwise switch out completely for the next process
    def handle_cpu_end_fcfs(self,event,print_event):
        event.get_process().compute_turnaround(event.get_t()+int(self.t_cs/2))

        # process has more cpu bursts to complete, so it just blocks on io
        # io_block event handles the context switching
        if len(event.process.get_bursts())-1 > 0:
            print(f"{event} {self.to_str_fcfs()}")
            heapq.heappush(self.event_queue,Event(event.get_t(), "io_block", self.active, self.t_cs))
            return
        
        # process is done, switching to next
        print(f"{event} {self.to_str_fcfs()}")
        event.get_process().complete_burst()

        # switch out actually happens at t+t_cs/2, switch in happens at t+t_cs/2 but waits t_cs/2 for cpu_start
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", self.active, self.t_cs))
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.ready_queue[0], self.t_cs))
        # only the switch out remains on the queue, otherwise done
        # this probably changes for preemptive algos
        elif len(self.ready_queue) == 0 and len(self.event_queue) == 1: 
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2),"terminate",None,self.t_cs))

    # when blocking on io, schedule an event to move the active process to io state. io_switch handles context switch overhead
    # queue io_end based on the io_burst time
    def handle_io_block_fcfs(self,event,print_event):
        print(f"{event} {self.to_str_fcfs()}")
        p = event.get_process()
        heapq.heappush(self.event_queue, Event(event.get_t(),"io_switch",p,self.t_cs))
        heapq.heappush(self.event_queue, Event(event.get_t()+p.get_bursts()[0][1]+int(self.t_cs/2), "io_end", p, self.t_cs))

    #  io completes -> add to queue -> check empty space
    def handle_io_end_fcfs(self,event,print_event):
        event.get_process().complete_burst()
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())

        self.ready_queue.append(event.get_process())
        print(f"{event} {self.to_str_fcfs()}")
        self.io_state = None
        # attempt to switch in if nothing is using the cpu and nothing is already trying to switch in 
        if not self.active and len(self.ready_queue) == 1:
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in", self.ready_queue[0], self.t_cs))

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               SJF
# --------------------------------------------------------------------------------------------------------------------------------------

    # switch in happens at t but stalls t_cs/2 ms before beginning cpu_start
    def handle_switch_in_sjf(self,event,print_event):
        if len(self.sjf_queue) > 0 and not self.active:
            self.sjf_queue[0].add_wait(event.get_t())
            if self.sjf_queue[0].get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1
            p = self.sjf_queue[0]
            self.active = p
            heapq.heappop(self.sjf_queue)
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    # switch out is reflected at the end of t+t_cs/2
    def handle_switch_out_sjf(self,event,print_event):
        if len(event.get_process().get_bursts()) > 0:
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
            # self.compute_simout()

    ''' each time a process gets added to the ready queue, we have to insert in tau-order '''
    def handle_arrival_sjf(self,event,print_event):
        heapq.heappush(self.sjf_queue, event.get_process())
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())

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

        # pop final cpu burst & append final wait time
        event.get_process().complete_burst()
        
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
        event.get_process().set_burst_arrival(event.get_t())
        heapq.heappush(self.sjf_queue, event.get_process())
        print(f"{event} {self.to_str_sjf()}")
        self.io_state = None
        if not self.active and len(self.sjf_queue) == 1:
            heapq.heappush(self.event_queue, Event(event.get_t(), "switch_in", self.sjf_queue[0], self.t_cs))

    def handle_tau_recalc(self, event, print_event):
        self.active.recalculate_tau()
        print(f"{event} {self.to_str_sjf()}")

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               SRT
# --------------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               RR
# --------------------------------------------------------------------------------------------------------------------------------------

    def preempt(self,event,print_event):
        if len(self.ready_queue) > 0:
            p = event.get_process()
            if p.get_type() == "CPU-bound": self.cpu_preempt+=1
            else: self.io_preempt += 1
            self.active.partial_burst(self.t_slice)
            print(f"time {event.get_t()}ms: Time slice expired; preempting process {p.get_pid()} with {p.get_bursts()[0][0]}ms remaining \
{self.to_str_fcfs()}")
            # update top burst
            self.active.begin_wait(event.get_t()+int(self.t_cs/2))

            # switch out
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", self.active, self.t_cs))
            # switch in 
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.ready_queue[0], self.t_cs))
        else:
            print(f"time {event.get_t()}ms: Time slice expired; no preemption because ready queue is empty [Q empty]")
            self.active.partial_burst(self.t_slice)
            burst_time = self.active.get_bursts()[0][0]
            if burst_time > self.t_slice:
                # queue preempt again in case something else arrives 
                heapq.heappush(self.event_queue,Event(event.get_t()+self.t_slice,"preempt",self.active, self.t_cs))
                # begin the wait time again when we add back to the queue
            else:
                heapq.heappush(self.event_queue,Event(event.get_t()+burst_time,"cpu_end",self.active, self.t_cs))

    # switch in happens at t but stalls t_cs/2 ms before beginning cpu_start
    def handle_switch_in_rr(self,event,print_event):
        if len(self.ready_queue) > 0 and not self.active:
            self.ready_queue[0].add_wait(event.get_t())
            if event.get_process().get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1
            p = self.ready_queue[0]
            self.active = p
            self.ready_queue.pop(0)
            # print(f"time {event.get_t()}: switch in occurred, {self.active.get_pid()} {self.to_str_fcfs()}")

            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    # switch out is reflected at the end of t+t_cs/2
    def handle_switch_out_rr(self,event,print_event):
        # add to ready queue if theres remaining cpu burst time, or more bursts in the future
        if len(event.get_process().get_bursts()) > 0:
            self.ready_queue.append(event.get_process())
        self.active=None
        # print(f"time {event.get_t()}ms: switch out occurred, {self.to_str_fcfs()}")

    # same as a switchout except don't add to the ready queue
    def io_active_switchout_rr(self,event,print_event):
        self.active=None

    def handle_io_switch_out_rr(self,event,print_event):
        self.io_state = self.active
        heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_out_io", self.active, self.t_cs))
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_in", self.ready_queue[0], self.t_cs))

    def rr(self,t_slice):
        self.t_slice=t_slice
        print(f"time 0ms: Simulator started for RR {self.to_str_fcfs()}")
        self.event_queue = [Event(p.get_arrival_time(), "arrival", p, self.t_cs) for p in self.processes]
        heapq.heapify(self.event_queue)

        # execute events as they arrive
        while (len(self.event_queue)>0):
            self.execute_event_rr(heapq.heappop(self.event_queue))

    def execute_event_rr(self, event):
        print_event = event.get_t() < 10000
        if event.type == "arrival":
            self.handle_arrival_rr(event,print_event)
        elif event.type == "switch_in":
            self.handle_switch_in_rr(event,print_event)
        elif event.type == "switch_out":
            self.handle_switch_out_rr(event,print_event)
        elif event.type == "io_switch":
            self.handle_io_switch_out_rr(event,print_event)
        elif event.type == "switch_out_io":
            self.io_active_switchout_rr(event,print_event)
        elif event.type == "cpu_start":
            self.handle_cpu_start_rr(event,print_event)
        elif event.type == "cpu_end": 
            self.handle_cpu_end_rr(event,print_event)
        elif event.type == "io_block":
            self.handle_io_block_rr(event,print_event)
        elif event.type == "io_end":
            self.handle_io_end_rr(event,print_event)
        elif event.type == "preempt":
            self.preempt(event,print_event)
        elif event.type == "terminate":
            print(f"time {event.get_t()}ms: Simulator ended for RR [Q empty]")
            self.termination = event.get_t()
            self.compute_simout_rr()

    def handle_arrival_rr(self,event,print_event):
        self.ready_queue.append(event.get_process())
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())
        print(f"{event} {self.to_str_fcfs()}")
        if not self.active:
            # add it to the active state in t_cs/2 ms, but remove from ready queue immediately
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in",event.get_process(),self.t_cs))
    
    # this changes. we don't know when the cpu will end
    def handle_cpu_start_rr(self,event,print_event):
        print(f"{event} {self.to_str_fcfs()}")
        burst_time = self.active.get_bursts()[0][0]
        if burst_time > self.t_slice:
            # queue preempt
            heapq.heappush(self.event_queue,Event(event.get_t()+self.t_slice,"preempt",self.active, self.t_cs))
        else:
            heapq.heappush(self.event_queue,Event(event.get_t()+burst_time,"cpu_end",self.active, self.t_cs))

    # cpu end: queue io event, switch out, switch in, queue new cpu start
    def handle_cpu_end_rr(self,event,print_event):
        event.get_process().compute_turnaround(event.get_t()+int(self.t_cs/2))

        # process has more cpu bursts to complete
        if len(event.process.get_bursts())-1 > 0:
            print(f"{event} {self.to_str_fcfs()}")
            heapq.heappush(self.event_queue,Event(event.get_t(), "io_block", self.active, self.t_cs))
            return
        # process is done, switching to next
        print(f"{event} {self.to_str_fcfs()}")

        event.get_process().complete_burst()

        # switch out actually happens at t+t_cs/2, switch in happens at t+t_cs/2 but waits t_cs/2 for cpu_start
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", self.active, self.t_cs))
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.ready_queue[0], self.t_cs))
        elif len(self.ready_queue) == 0 and len(self.event_queue) == 1: # only the switch out remains on the queue
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2),"terminate",None,self.t_cs))

    def handle_io_block_rr(self,event,print_event):
        print(f"{event} {self.to_str_fcfs()}")
        p = event.get_process()
        heapq.heappush(self.event_queue, Event(event.get_t(),"io_switch",p,self.t_cs))
        heapq.heappush(self.event_queue, Event(event.get_t()+p.get_bursts()[0][1]+int(self.t_cs/2), "io_end", p, self.t_cs))

    #  io completes -> add to queue -> check empty space
    def handle_io_end_rr(self,event,print_event):
        event.get_process().complete_burst()
        event.get_process().begin_wait(event.get_t())
        self.ready_queue.append(event.get_process())
        event.get_process().set_burst_arrival(event.get_t())

        print(f"{event} {self.to_str_fcfs()}")
        self.io_state = None
        # attempt to switch in if nothing is already trying to switch in 
        if not self.active and len(self.ready_queue) == 1:
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in", self.ready_queue[0], self.t_cs))

    def ceil_help(self, val):
        return math.ceil(val * 1000) / 1000

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

        cpu_utilization = self.burst_time / self.termination
        overall_avg /= total_bursts if total_bursts > 0 else 0
        cpu_wait /= cpu_bursts if cpu_bursts > 0 else 0
        io_wait /= io_bursts if io_bursts > 0 else 0
        turnaround_avg /= total_bursts if total_bursts > 0 else 0
        cpu_turnaround /= cpu_bursts if cpu_bursts > 0 else 0
        io_turnaround /= io_bursts if io_bursts > 0 else 0
        
        print("-- CPU utilization: {:.3f}%".format(self.ceil_help(cpu_utilization*100)))
        print("-- CPU-bound average wait time: {:.3f} ms".format(self.ceil_help(cpu_wait)))
        print("-- I/O-bound average wait time: {:.3f} ms".format(self.ceil_help(io_wait)))
        print("-- overall average wait time: {:.3f} ms".format(self.ceil_help(overall_avg)))
        print("-- CPU-bound average turnaround time: {:.3f} ms".format(self.ceil_help(cpu_turnaround)))
        print("-- I/O-bound average turnaround time: {:.3f} ms".format(self.ceil_help(io_turnaround)))
        print("-- overall average turnaround time: {:.3f} ms".format(self.ceil_help(turnaround_avg)))
        print(f"-- CPU-bound number of context switches: {self.cpu_context}")
        print(f"-- I/O-bound number of context switches: {self.io_context}")
        print(f"-- overall number of context switches: {self.cpu_context + self.io_context}")
        print(f"-- CPU-bound number of preemptions: {self.cpu_preempt}")
        print(f"-- I/O-bound number of preemptions: {self.io_preempt}")
        print(f"-- overall number of preemptions: {self.cpu_preempt+self.io_preempt}")


    def compute_simout_rr(self):
        self.compute_simout()
        cpu_bound_ts = io_bound_ts = cpu_bursts = io_bursts = all_bursts = 0
        for p in self.original_processes:
            for b in p.get_bursts():
                if p.get_type() == "CPU-bound":
                    if b[0] <= self.t_slice:
                        cpu_bound_ts+=1
                    cpu_bursts += 1
                else:
                    if b[0] <= self.t_slice:
                        io_bound_ts+=1
                    io_bursts+=1
                all_bursts += 1
        cpu_pct = self.ceil_help(100*cpu_bound_ts/cpu_bursts) if cpu_bursts > 0 else 0
        io_pct = self.ceil_help(100*io_bound_ts/io_bursts) if io_bursts > 0 else 0
        overall_pct = self.ceil_help(100*(cpu_bound_ts+io_bound_ts)/all_bursts) if all_bursts > 0 else 0
        print("-- CPU-bound percentage of CPU bursts completed within one time slice: {:.3f}%".format(cpu_pct))
        print("-- CPU-bound percentage of CPU bursts completed within one time slice:  {:.3f}%".format(io_pct))
        print("-- overall percentage of CPU bursts completed within one time slice: {:.3f}%".format(overall_pct))

                
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