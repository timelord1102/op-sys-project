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
        self.switching = False
        self.rr_alt = False
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
    ''' switch in a process if there's nothing running and nothing actively switching in '''
    def handle_switch_in_fcfs(self,event,print_event):
        if len(self.ready_queue) > 0 and not self.active and not self.switching:
            self.switching = True
            self.ready_queue[0].add_wait(event.get_t())
            if self.ready_queue[0].get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1
            p = self.ready_queue[0]
            self.active = p
            self.ready_queue.pop(0)
            # queue a cpu_start at time t+t_cs/2.
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    ''' switch out is reflected at the end of t+t_cs/2. we only add back to the ready queue if theres more than one
     burst remaining. '''
    def handle_switch_out_fcfs(self,event,print_event):
        if len(event.get_process().get_bursts()) > 0:
            self.ready_queue.append(event.get_process())
        self.switching = False
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t(), "switch_in", self.ready_queue[0], self.t_cs))

    ''' switch active state to the io state '''
    def io_active_switchout_fcfs(self,event,print_event):
        self.switching = False
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t(), "switch_in", self.ready_queue[0], self.t_cs))

    ''' switch the active state out, and bring the next process in if possible'''
    def handle_io_switch_out_fcfs(self,event,print_event):
        self.io_state = self.active
        self.active = None # active is no longer running/completing bursts
        self.switching = True
        heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_out_io", self.io_state, self.t_cs))


    ''' driver function: execute each event in the queue until it's empty '''
    def fcfs(self):
        print(f"time 0ms: Simulator started for FCFS {self.to_str_fcfs()}")
        self.event_queue = [Event(p.get_arrival_time(), "arrival", p, self.t_cs) for p in self.processes]
        heapq.heapify(self.event_queue)

        # execute events as they arrive
        while (len(self.event_queue)>0):
            self.execute_event_fcfs(heapq.heappop(self.event_queue))

    def execute_event_fcfs(self, event):
        # print event isnt used yet, but we only need to print things before 10000ms
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
            print(f"time {event.get_t()}ms: Simulator ended for FCFS [Q empty]\n")
            self.termination = event.get_t()
            # self.compute_simout()

    ''' add process to the ready queue, and attempt to move into the running state '''
    def handle_arrival_fcfs(self,event,print_event):
        self.ready_queue.append(event.get_process())

        # set the starting time for wait and turnaround times for this cpu burst
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())
        if print_event:
            print(f"{event.to_str()} {self.to_str_fcfs()}")
        if not self.active and not self.switching:
            # add to the active state in t_cs/2 ms, but remove from ready queue immediately
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in",event.get_process(),self.t_cs))

    ''' queue cpu ending event '''
    def handle_cpu_start_fcfs(self,event,print_event):
        if print_event:
            print(f"{event.to_str()} {self.to_str_fcfs()}")
        self.switching = False
        # self.active is a process, which stores bursts as [[cpu_burst,io_burst]...,[cpu_burst]]
        heapq.heappush(self.event_queue,Event(event.get_t()+self.active.get_bursts()[0][0],"cpu_end",self.active, self.t_cs))

    ''' end: queue io event if if has one, otherwise switch out completely for the next process '''
    def handle_cpu_end_fcfs(self,event,print_event):
        event.get_process().compute_turnaround(event.get_t()+int(self.t_cs/2))

        # process has more cpu bursts to complete, so it just blocks on io
        # io_block event handles the context switching
        if len(event.process.get_bursts())-1 > 0:
            if print_event:
                print(f"{event.to_str()} {self.to_str_fcfs()}")
            heapq.heappush(self.event_queue,Event(event.get_t(), "io_block", self.active, self.t_cs))
            return

        # process is done, switching to next
        print(f"{event.to_str()} {self.to_str_fcfs()}")
        event.get_process().complete_burst()

        active = self.active
        self.active = None
        self.switching = True
        # switch out actually happens at t+t_cs/2, switch in happens at t+t_cs/2 but waits t_cs/2 for cpu_start
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", active, self.t_cs))
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.ready_queue[0], self.t_cs))
        # only the switch out remains on the queue, otherwise done
        elif len(self.ready_queue) == 0 and len(self.event_queue) == 1:
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2),"terminate",None,self.t_cs))

    ''' schedule a switch out from the active state, and schedule an i/o completion event '''
    def handle_io_block_fcfs(self,event,print_event):
        if print_event:
            print(f"{event.to_str()} {self.to_str_fcfs()}")
        p = event.get_process()
        heapq.heappush(self.event_queue, Event(event.get_t(),"io_switch",p,self.t_cs))
        heapq.heappush(self.event_queue, Event(event.get_t()+p.get_bursts()[0][1]+int(self.t_cs/2), "io_end", p, self.t_cs))

    ''' io completes -> add to queue -> switch in if possible '''
    def handle_io_end_fcfs(self,event,print_event):
        event.get_process().complete_burst()
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())

        self.ready_queue.append(event.get_process())
        if print_event:
            print(f"{event.to_str()} {self.to_str_fcfs()}")
        self.io_state = None
        # attempt to switch in if nothing is using the cpu and nothing is already trying to switch in
        if not self.active and not self.switching:
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in", self.ready_queue[0], self.t_cs))

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               SJF
# --------------------------------------------------------------------------------------------------------------------------------------

    # switch in happens at t but stalls t_cs/2 ms before beginning cpu_start
    def handle_switch_in_sjf(self,event,print_event):
        if len(self.sjf_queue) > 0 and not self.active and not self.switching:
            self.switching = True
            self.sjf_queue[0].add_wait(event.get_t())
            if self.sjf_queue[0].get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1
            p = self.sjf_queue[0]
            heapq.heappop(self.sjf_queue)
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    # switch out is reflected at the end of t+t_cs/2
    def handle_switch_out_sjf(self,event,print_event):
        if len(event.get_process().get_bursts()) > 0:
            heapq.heappush(self.sjf_queue,event.get_process())
        self.switching = False
        if len(self.sjf_queue) > 0 and print_event:
            heapq.heappush(self.event_queue,Event(event.get_t(), "switch_in", self.sjf_queue[0], self.t_cs))

    def handle_io_switch_out_sjf(self,event,print_event):
        self.io_state = self.active
        self.active = None
        self.switching = True
        heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_out_io", self.io_state, self.t_cs))


    def io_active_switchout_sjf(self,event,print_event):
        self.switching = False
        if len(self.sjf_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t(), "switch_in", self.sjf_queue[0], self.t_cs))

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
            print(f"time {event.get_t()}ms: Simulator ended for SJF [Q empty]\n")
            self.termination = event.get_t()
            

    ''' each time a process gets added to the ready queue, we have to insert in tau-order '''
    def handle_arrival_sjf(self,event,print_event):
        heapq.heappush(self.sjf_queue, event.get_process())
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())

        if print_event:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")

        if not self.active and not self.switching:
            # add it to the active state in t_cs/2 ms, but remove from ready queue immediately
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in",event.get_process(),self.t_cs))

    def handle_cpu_start_sjf(self,event,print_event):
        self.switching = False
        self.active = event.get_process()
        if print_event:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")
        heapq.heappush(self.event_queue,Event(event.get_t()+self.active.get_bursts()[0][0],"cpu_end",self.active, self.t_cs))

    # cpu end: queue io event, switch out, switch in, queue new cpu start
    def handle_cpu_end_sjf(self,event,print_event):
        event.get_process().compute_turnaround(event.get_t()+int(self.t_cs/2))
        # process has more cpu bursts to complete
        if len(event.process.get_bursts())-1 > 0:
            if print_event:
                print(f"{event.to_str_tau()} {self.to_str_sjf()}")
            heapq.heappush(self.event_queue,Event(event.get_t(), "tau_recalc", self.active, self.t_cs))
            heapq.heappush(self.event_queue,Event(event.get_t(), "io_block", self.active, self.t_cs))
            return
        print(f"{event.to_str_tau()} {self.to_str_sjf()}")

        # pop final cpu burst & append final wait time
        event.get_process().complete_burst()

        active = self.active
        self.active = None
        self.switching = True
        # switch out actually happens at t+t_cs/2, switch in happens at t+t_cs/2 but waits t_cs/2 for cpu_start
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", active, self.t_cs))
        if len(self.sjf_queue) > 0:
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.sjf_queue[0], self.t_cs))
        elif len(self.ready_queue) == 0 and len(self.event_queue) == 1: # only the switch out remains on the queue
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2),"terminate",None,self.t_cs))

    def handle_io_block_sjf(self,event,print_event):
        if print_event:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")
        p = event.get_process()
        heapq.heappush(self.event_queue, Event(event.get_t(),"io_switch",p,self.t_cs))
        heapq.heappush(self.event_queue, Event(event.get_t()+p.get_bursts()[0][1]+int(self.t_cs/2), "io_end", p, self.t_cs))

    #  io completes -> add to queue -> check empty space
    def handle_io_end_sjf(self,event,print_event):
        event.get_process().complete_burst()
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())
        heapq.heappush(self.sjf_queue, event.get_process())
        if print_event:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")
        self.io_state = None
        if not self.active and not self.switching:
            heapq.heappush(self.event_queue, Event(event.get_t(), "switch_in", self.sjf_queue[0], self.t_cs))

    def handle_tau_recalc(self, event, print_event):
        self.active.recalculate_tau()
        if print_event and self.active.alpha != -1:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               SRT
# --------------------------------------------------------------------------------------------------------------------------------------

    def preempt_srt(self, event, print_event):
        self.switching=True
        p = self.active
        self.active = None
        p.begin_wait(event.get_t()+int(self.t_cs/2))
        if p.get_type() == "CPU-bound": self.cpu_preempt+=1
        else: self.io_preempt += 1
        # switch out
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", p, self.t_cs))
        # switch in
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.sjf_queue[0], self.t_cs))

    # switch in happens at t but stalls t_cs/2 ms before beginning cpu_start
    def handle_switch_in_srt(self,event,print_event):
        if len(self.sjf_queue) > 0 and not self.active and not self.switching:
            self.switching = True
            p = self.sjf_queue[0]

            p.add_wait(event.get_t())
            if p.get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1

            heapq.heappop(self.sjf_queue)
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    # switch out is reflected at the end of t+t_cs/2
    def handle_switch_out_srt(self,event,print_event):
        if len(event.get_process().get_bursts()) > 0:
            heapq.heappush(self.sjf_queue,event.get_process())
        self.switching = False
        if len(self.sjf_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t(), "switch_in", self.sjf_queue[0], self.t_cs))

    def handle_io_switch_out_srt(self,event,print_event):
        self.io_state = event.get_process()
        self.active = None
        self.switching = True
        heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_out_io", self.io_state, self.t_cs))


    def io_active_switchout_srt(self,event,print_event):
        self.switching = False
        if len(self.sjf_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t(), "switch_in", self.sjf_queue[0], self.t_cs))

    def srt(self):
        print(f"time 0ms: Simulator started for SRT {self.to_str_sjf()}")
        self.event_queue = [Event(p.get_arrival_time(), "arrival", p, self.t_cs) for p in self.processes]
        heapq.heapify(self.event_queue)

        # execute events as they arrive
        while (len(self.event_queue)>0):
            self.execute_event_srt(heapq.heappop(self.event_queue))

    def execute_event_srt(self, event):
        print_event = event.get_t() < 10000
        if event.type == "arrival":
            self.handle_arrival_srt(event,print_event)
        elif event.type == "switch_in":
            self.handle_switch_in_srt(event,print_event)
        elif event.type == "switch_out":
            self.handle_switch_out_srt(event,print_event)
        elif event.type == "io_switch":
            self.handle_io_switch_out_srt(event,print_event)
        elif event.type == "switch_out_io":
            self.io_active_switchout_srt(event,print_event)
        elif event.type == "cpu_start":
            self.handle_cpu_start_srt(event,print_event)
        elif event.type == "cpu_end":
            self.handle_cpu_end_srt(event,print_event)
        elif event.type == "io_block":
            self.handle_io_block_srt(event,print_event)
        elif event.type == "io_end":
            self.handle_io_end_srt(event,print_event)
        elif event.type == "tau_recalc":
            self.handle_tau_recalc_srt(event,print_event)
        elif event.type == "preempt":
            self.preempt_srt(event,print_event)
        elif event.type == "terminate":
            print(f"time {event.get_t()}ms: Simulator ended for SRT [Q empty]\n")
            self.termination = event.get_t()
            # self.compute_simout()

    ''' each time a process gets added to the ready queue, we have to insert in tau-order '''
    ''' this will change, have to account for preemptions '''
    def handle_arrival_srt(self,event,print_event):
        heapq.heappush(self.sjf_queue, event.get_process())
        if print_event:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")

        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())

        if self.active:
            if self.active.alpha == -1:
                self.active.partial_burst(event.get_t()-self.active.cpu_start)
                self.active.set_cpu_start(event.get_t())
                if event.get_process() < self.active:
                    heapq.heappush(self.event_queue, Event(event.get_t(),"preempt",self.active,self.t_cs))
            else:
                remaining = self.active.calc_remaining_tau(event.get_t())
                if remaining > event.get_process().get_tau():
                    self.active.set_remaining_tau(remaining)
                    self.active.partial_burst(event.get_t()-self.active.cpu_start)
                    heapq.heappush(self.event_queue, Event(event.get_t(),"preempt",self.active,self.t_cs))
        else:
            # add it to the active state in t_cs/2 ms, but remove from ready queue immediately
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in",event.get_process(),self.t_cs))

    ''' we don't know when the cpu end will happen, so this will change'''
    def handle_cpu_start_srt(self,event,print_event):
        self.switching = False
        if print_event:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")
        self.active = event.get_process()
        self.active.set_cpu_start(event.get_t())
        # this will only happen from context switch timings, otherwise arrival/io switch in handles this
        if self.active.alpha == -1 and len(self.sjf_queue) > 0 and self.sjf_queue[0] < self.active:
                print(self.sjf_queue[0].bursts[0],self.active.bursts[0])
                if print_event:
                    print(f"time {event.get_t()}ms: Process {self.sjf_queue[0].get_pid()} will preempt \
{event.get_process().get_pid()} {self.to_str_sjf()}")
                heapq.heappush(self.event_queue, Event(event.get_t(),"preempt",self.active,self.t_cs))

        elif self.active.alpha != -1 and len(self.sjf_queue) > 0 and self.sjf_queue[0].get_remaining_tau() < event.get_process().get_remaining_tau():
            if print_event:
                print(f"time {event.get_t()}ms: Process {self.sjf_queue[0].get_pid()} (tau {self.sjf_queue[0].get_tau()}ms) will preempt \
{event.get_process().get_pid()} {self.to_str_sjf()}")
            heapq.heappush(self.event_queue, Event(event.get_t(),"preempt",self.active,self.t_cs))
        
        else:
            heapq.heappush(self.event_queue,Event(event.get_t()+self.active.get_bursts()[0][0],"cpu_end",self.active, self.t_cs))

    '''
    cpu end:
      check if the process is actually ending (must be in active spot, partial burst should bring it to 0)
      if bursts[0][0] == 0:
        block on io
        bring the next process in
    '''
    def handle_cpu_end_srt(self,event,print_event):
        p = event.get_process()
        if self.active and p.get_pid() == self.active.get_pid():
            p.partial_burst(event.get_t()-p.cpu_start)
            # partial_burst updates the top burst time, so we have to adjust cpu_start
            p.set_remaining_tau(p.calc_remaining_tau(event.get_t()))
            p.set_cpu_start(event.get_t())

            # burst completed, more to complete
            if p.bursts[0][0] == 0 and len(event.process.get_bursts())-1 > 0:
                if print_event:
                    print(f"{event.to_str_tau()} {self.to_str_sjf()}")
                p.compute_turnaround(event.get_t()+int(self.t_cs/2))
                heapq.heappush(self.event_queue,Event(event.get_t(), "tau_recalc", self.active, self.t_cs))
                heapq.heappush(self.event_queue,Event(event.get_t(), "io_block", self.active, self.t_cs))

            # burst completed, no more to complete
            elif p.bursts[0][0] == 0:
                print(f"{event.to_str_tau()} {self.to_str_sjf()}")
                p.compute_turnaround(event.get_t()+int(self.t_cs/2))
                # pop final cpu burst & append final wait time
                p.complete_burst()
                self.switching=True
                active = self.active
                self.active = None
                # switch out actually happens at t+t_cs/2, switch in happens at t+t_cs/2 but waits t_cs/2 for cpu_start
                heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", active, self.t_cs))
                if len(self.sjf_queue) > 0:
                    heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.sjf_queue[0], self.t_cs))
                elif len(self.ready_queue) == 0 and len(self.event_queue) == 1: # only the switch out remains on the queue
                    heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2),"terminate",None,self.t_cs))


    def handle_io_block_srt(self,event,print_event):
        if print_event:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")
        p = event.get_process()
        heapq.heappush(self.event_queue, Event(event.get_t(),"io_switch",p,self.t_cs))
        heapq.heappush(self.event_queue, Event(event.get_t()+p.get_bursts()[0][1]+int(self.t_cs/2), "io_end", p, self.t_cs))

    '''
    io_end:
      always add to ready queue, complete cpu burst, set io_state to None.
      if there's an active process, compare its remaining time to the process tau
        if process tau is less than remaining, preempt
      if there's no active process, switch back into the cpu

    '''
    def handle_io_end_srt(self,event,print_event):
        p = event.get_process()
        p.complete_burst()
        p.begin_wait(event.get_t())
        p.set_burst_arrival(event.get_t())
        heapq.heappush(self.sjf_queue, event.get_process())
        self.io_state = None
        if self.active and not self.switching:
            if self.active.alpha == -1:
                self.active.partial_burst(event.get_t()-self.active.cpu_start)
                self.active.set_cpu_start(event.get_t())
                if event.get_process() < self.active:
                    if print_event:
                        print(f"time {event.get_t()}ms: Process {p.get_pid()} completed I/O; preempting \
{self.active.get_pid()} {self.to_str_sjf()}")  
                    heapq.heappush(self.event_queue, Event(event.get_t(),"preempt",self.active,self.t_cs))
                return
            remaining = self.active.calc_remaining_tau(event.get_t())
            # print(f"time {event.get_t()}ms: predicted remaining time: {remaining}")
            if p.get_tau() < remaining:
                self.active.set_remaining_tau(remaining)
                self.active.partial_burst(event.get_t()-self.active.cpu_start)
                if print_event:
                    print(f"time {event.get_t()}ms: Process {p.get_pid()} (tau {p.get_tau()}ms) completed I/O; preempting \
{self.active.get_pid()} (predicted remaining time {remaining}ms) {self.to_str_sjf()}")
                heapq.heappush(self.event_queue, Event(event.get_t(), "preempt", self.active, self.t_cs))
                return
        if print_event:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")
        if not self.active:
            heapq.heappush(self.event_queue, Event(event.get_t(), "switch_in", self.sjf_queue[0], self.t_cs))

    def handle_tau_recalc_srt(self, event, print_event):
        self.active.recalculate_tau()
        if print_event and self.active.alpha != -1:
            print(f"{event.to_str_tau()} {self.to_str_sjf()}")

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                               RR
# --------------------------------------------------------------------------------------------------------------------------------------

    def preempt(self,event,print_event):
        if len(self.ready_queue) > 0:
            p = event.get_process()
            if p.get_type() == "CPU-bound": self.cpu_preempt+=1
            else: self.io_preempt += 1
            self.active.partial_burst(self.t_slice)
            if print_event:
                print(f"time {event.get_t()}ms: Time slice expired; preempting process {p.get_pid()} with {p.get_bursts()[0][0]}ms remaining \
{self.to_str_fcfs()}")
            # update top burst
            self.active.begin_wait(event.get_t()+int(self.t_cs/2))
            active = self.active
            self.active = None
            self.switching = True
            # switch out
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", active, self.t_cs))
            # switch in
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.ready_queue[0], self.t_cs))
        else:
            if print_event:
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
        if len(self.ready_queue) > 0 and not self.active and not self.switching:
            self.switching = True
            p = self.ready_queue[0]
            p.add_wait(event.get_t())
            if event.get_process().get_type() == "CPU-bound": self.cpu_context+=1
            else: self.io_context+=1

            self.ready_queue.pop(0)
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "cpu_start", p, self.t_cs))

    # switch out is reflected at the end of t+t_cs/2
    def handle_switch_out_rr(self,event,print_event):
        # add to ready queue if theres remaining cpu burst time, or more bursts in the future
        if len(event.get_process().get_bursts()) > 0:
            if not self.rr_alt:
                self.ready_queue.append(event.get_process())
            else:
                if len(self.ready_queue) > 1:
                    self.ready_queue.insert(1, event.get_process())    
                else:
                    self.ready_queue.append(event.get_process())
        self.switching = False
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t(), "switch_in", self.ready_queue[0], self.t_cs))

    # same as a switchout except don't add to the ready queue
    def io_active_switchout_rr(self,event,print_event):
        self.switching=False
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue,Event(event.get_t(), "switch_in", self.ready_queue[0], self.t_cs))

    def handle_io_switch_out_rr(self,event,print_event):
        self.io_state = self.active
        self.active = None
        self.switching = True
        heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2), "switch_out_io", self.io_state, self.t_cs))


    def rr(self,t_slice,rr_alt):
        self.rr_alt = rr_alt
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

    def handle_arrival_rr(self,event,print_event):
        self.ready_queue.append(event.get_process())
        event.get_process().begin_wait(event.get_t())
        event.get_process().set_burst_arrival(event.get_t())
        if print_event:
            print(f"{event.to_str()} {self.to_str_fcfs()}")
        if not self.active and not self.switching:
            # add it to the active state in t_cs/2 ms, but remove from ready queue immediately
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in",event.get_process(),self.t_cs))

    # this changes. we don't know when the cpu will end
    def handle_cpu_start_rr(self,event,print_event):
        if print_event:
            print(f"{event.to_str()} {self.to_str_fcfs()}")
        self.active = event.get_process()
        self.switching = False
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
            if print_event:
                print(f"{event.to_str()} {self.to_str_fcfs()}")
            heapq.heappush(self.event_queue,Event(event.get_t(), "io_block", self.active, self.t_cs))
            return
        # process is done, switching to next
        print(f"{event.to_str()} {self.to_str_fcfs()}")

        event.get_process().complete_burst()

        active = self.active
        self.active = None
        self.switching = True
        # switch out actually happens at t+t_cs/2, switch in happens at t+t_cs/2 but waits t_cs/2 for cpu_start
        heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_out", active, self.t_cs))
        if len(self.ready_queue) > 0:
            heapq.heappush(self.event_queue, Event(event.get_t()+int(self.t_cs/2),"switch_in", self.ready_queue[0], self.t_cs))
        elif len(self.ready_queue) == 0 and len(self.event_queue) == 1: # only the switch out remains on the queue
            heapq.heappush(self.event_queue,Event(event.get_t()+int(self.t_cs/2),"terminate",None,self.t_cs))

    def handle_io_block_rr(self,event,print_event):
        if print_event:
            print(f"{event.to_str()} {self.to_str_fcfs()}")
        p = event.get_process()
        heapq.heappush(self.event_queue, Event(event.get_t(),"io_switch",p,self.t_cs))
        heapq.heappush(self.event_queue, Event(event.get_t()+p.get_bursts()[0][1]+int(self.t_cs/2), "io_end", p, self.t_cs))

    #  io completes -> add to queue -> check empty space
    def handle_io_end_rr(self,event,print_event):
        event.get_process().complete_burst()
        event.get_process().begin_wait(event.get_t())
        self.ready_queue.append(event.get_process())
        event.get_process().set_burst_arrival(event.get_t())
        if print_event:
            print(f"{event.to_str()} {self.to_str_fcfs()}")
        self.io_state = None
        # attempt to switch in if nothing is already trying to switch in
        if not self.active and not self.switching:
            heapq.heappush(self.event_queue, Event(event.get_t(),"switch_in", self.ready_queue[0], self.t_cs))

    def ceil_help(self, val):
        return math.ceil(val * 1000) / 1000

    def compute_simout(self):
        simout = ''
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

        cpu_utilization = self.burst_time / self.termination if self.termination > 0 else 0
        overall_avg = overall_avg/total_bursts if total_bursts > 0 else 0
        cpu_wait = cpu_wait/cpu_bursts if cpu_bursts > 0 else 0
        io_wait = io_wait/io_bursts if io_bursts > 0 else 0
        turnaround_avg = turnaround_avg/total_bursts if total_bursts > 0 else 0
        cpu_turnaround = cpu_turnaround/cpu_bursts if cpu_bursts > 0 else 0
        io_turnaround = io_turnaround/io_bursts if io_bursts > 0 else 0

        simout += "-- CPU utilization: {:.3f}%\n".format(self.ceil_help(cpu_utilization*100))
        simout += "-- CPU-bound average wait time: {:.3f} ms\n".format(self.ceil_help(cpu_wait))
        simout += "-- I/O-bound average wait time: {:.3f} ms\n".format(self.ceil_help(io_wait))
        simout += "-- overall average wait time: {:.3f} ms\n".format(self.ceil_help(overall_avg))
        simout += "-- CPU-bound average turnaround time: {:.3f} ms\n".format(self.ceil_help(cpu_turnaround))
        simout += "-- I/O-bound average turnaround time: {:.3f} ms\n".format(self.ceil_help(io_turnaround))
        simout += "-- overall average turnaround time: {:.3f} ms\n".format(self.ceil_help(turnaround_avg))
        simout += f"-- CPU-bound number of context switches: {self.cpu_context}\n"
        simout += f"-- I/O-bound number of context switches: {self.io_context}\n"
        simout += f"-- overall number of context switches: {self.cpu_context + self.io_context}\n"
        simout += f"-- CPU-bound number of preemptions: {self.cpu_preempt}\n"
        simout += f"-- I/O-bound number of preemptions: {self.io_preempt}\n"
        simout += f"-- overall number of preemptions: {self.cpu_preempt+self.io_preempt}\n"
        return simout


    def compute_simout_rr(self):
        simout = self.compute_simout()
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
        simout += "-- CPU-bound percentage of CPU bursts completed within one time slice: {:.3f}%\n".format(cpu_pct)
        simout += "-- I/O-bound percentage of CPU bursts completed within one time slice: {:.3f}%\n".format(io_pct)
        simout += "-- overall percentage of CPU bursts completed within one time slice: {:.3f}%\n".format(overall_pct)
        return simout

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
