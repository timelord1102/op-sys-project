import io
import re


class AlgorithmData:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.num_cpu_processes = 0
        self.num_io_processes = 0
        self.cpu_total_bursts = 0
        self.io_total_bursts = 0
        self.cpu_total_wait = 0
        self.io_total_wait = 0
        self.cpu_total_turnaround = 0
        self.io_total_turnaround = 0
        self.cpu_context_switches = 0
        self.io_context_switches = 0
        self.cpu_preemptions = 0
        self.io_preemptions = 0
        self.total_run_time = 0
        self.cpu_busy = 0;

    def __str__(self):
        s = "-- CPU utilization: " + "{:.3f}".format((self.cpu_busy/self.total_run_time if self.total_run_time != 0 else 0)*100) + "%\n"
        s += "-- CPU-bound average wait time: " + "{:.3f}".format(self.cpu_total_wait/self.cpu_context_switches if self.cpu_context_switches != 0 else 0) + " ms\n"
        s += "-- IO-bound average wait time: " + "{:.3f}".format(self.io_total_wait/self.io_context_switches if self.io_context_switches != 0 else 0) + " ms\n"
        s += "-- overall average wait time: " + "{:.3f}".format(round((self.cpu_total_wait + self.io_total_wait)/(self.cpu_context_switches + self.io_context_switches) if (self.cpu_context_switches + self.io_context_switches) != 0 else 0, 3)) + " ms\n"
        s += "-- CPU-bound average turnaround time: " + "{:.3f}".format(round(self.cpu_total_turnaround/self.cpu_context_switches if self.cpu_context_switches != 0 else 0, 3)) + " ms\n"
        s += "-- IO-bound average turnaround time: " + "{:.3f}".format(round(self.io_total_turnaround/self.io_context_switches if self.io_context_switches != 0 else 0, 3)) + " ms\n"
        s += "-- overall average turnaround time: " + "{:.3f}".format(round((self.cpu_total_turnaround + self.io_total_turnaround)/(self.cpu_context_switches + self.io_context_switches) if (self.cpu_context_switches + self.io_context_switches) != 0 else 0, 3)) + " ms\n"
        s += "-- CPU-bound number of context switches: " + str(self.cpu_context_switches) + "\n"
        s += "-- IO-bound number of context switches: " + str(self.io_context_switches) + "\n"
        s += "-- overall number of context switches: " + str(self.cpu_context_switches + self.io_context_switches) + "\n"
        s += "-- CPU-bound number of preemptions: " + str(self.cpu_preemptions) + "\n"
        s += "-- IO-bound number of preemptions: " + str(self.io_preemptions) + "\n"
        s += "-- overall number of preemptions: " + str(self.cpu_preemptions + self.io_preemptions) + "\n"
        return s
