from time import *
from tkinter import *
from threading import *

class Process:
    def __init__(self, id, arrival_time, burst_time, priority, start_wait_time, end_wait_time):
        """
        Initiate process
        """
        # process unique id
        self.id = id
        # time the process arrived to the ready queue
        self.arrival_time = arrival_time
        # total amount of time the process will run
        self.burst_time = burst_time
        # time remaining for the process to finish running
        self.remaining_time = burst_time
        # priority of the process (for example: 1 have higher priority that 2)
        self.priority = priority
        # time the process will stop running in the cpu and leave to enter a waiting queue
        self.start_waiting_time = start_wait_time
        # time the process will wait in the waiting queue before being released to the ready queue
        self.end_waiting_time = end_wait_time

    def __str__(self):
        """
        prints the process attributes when process is called
        skips printing priority, start_waiting_time, end_waiting_time variables if not specified by user (None)
        """
        string = f"process: {self.id} with arrival_time: {self.arrival_time}, burst_time: {self.burst_time}, remaining_time: {self.remaining_time}"
        if self.priority:
            string += f", priority: {self.priority}"
        if self.start_waiting_time and self.end_waiting_time:
            string += f", start waiting time: {self.start_waiting_time}, end waiting time: {self.end_waiting_time}"
        return string

class CpuScheduler:
    def __init__(self, scheduling_algorithm):
        # job queue to store new processes until their arrival time comes
        self.job_queue = []
        # ready queue to store processes whose arrival time have arrived
        self.ready_queue = []
        # the current running process on the cpu
        self.current_process = None
        # waiting queue to store all processes that are waiting for an input. also the time left for the input arrival is stored too
        self.waiting_queue = {} # waiting queue
        # the scheduling algorithm
        self.scheduling_algorithm = scheduling_algorithm

        # some colors and a reset value for better looking terminal
        self.RESET = "\033[0m" # reset colors
        self.GREEN = "\033[32m" # running queue
        self.YELLOW = "\033[33m" # ready queue
        self.RED = "\033[31m"  # waiting queue

        # initiate a current second
        self.current_second = -1
        # initiate a previous second
        self.previous_second = -1
        # a switch to the timer (either ON (True) or OFF (false))
        self.timer_switch = False

        # start a thread to print the time every second if timer switch is ON
        Thread(target=self.timer).start()
        # start a thread that will print the status of processes and manage them every second
        Thread(target=self.main).start()

    def timer(self):
        """
        print the current second when the switch is on
        """
        while True:
            while self.timer_switch:
                if self.current_second != -1:
                    print(f"\n\n{self.current_second}", end='')
                    sleep(1)
                    self.current_second += 1
                else:
                    self.current_second += 1

    def add_process(self, process):
        """
        add a new process to the job queue
        """
        print(f"\n{self.RED}{process} has been added to the job queue{self.RESET}", end='')
        self.job_queue.append(process)

    def start_pause_cpu_scheduler_timer(self):
        """
        Responsible for starting or pausing the scheduler timer
        """
        if self.timer_switch:
            self.timer_switch = False
        else:
            self.timer_switch = True

    def main(self):
        while True:
            # only continue if current second is different from previous second
            # this prevents code from looping while a second haven't passed yet
            if self.current_second != self.previous_second:
                if self.job_queue:
                    """
                    move a process from job queue to ready queue if its arrival time comes
                    """
                    for process in self.job_queue:
                        if process.arrival_time <= self.current_second:
                            print(f"\n{self.YELLOW}{process} has been moved from job queue to ready queue{self.RESET}", end='')
                            self.ready_queue.append(process)
                            self.job_queue.remove(process)

                if self.waiting_queue:
                    """
                    Move process out of the waiting queue and into the ready queue again when its end time have arrived
                    """
                    for process in list(self.waiting_queue.keys()):
                        self.waiting_queue[process] -= 1
                        if self.waiting_queue[process] == 0:
                            print(f"\n{self.YELLOW}{process} has been moved from waiting queue to ready queue{self.RESET}",end='')
                            self.ready_queue.append(process)
                            self.waiting_queue.pop(process)

                if self.current_process:
                    """
                    decrement one second from the current running process time and marks it as completed if process time == 0
                    """
                    self.current_process.remaining_time -= 1
                    if self.current_process.remaining_time == 0:
                        print(f"\n{self.GREEN}{self.current_process} has been completed after {self.current_second - self.current_process.arrival_time} seconds.{self.RESET}", end='')
                        self.current_process = None

                if self.current_process:
                    """
                    Move a running process to a waiting queue if its start waiting time have arrived
                    """
                    if self.current_process.start_waiting_time:
                        if self.current_process.start_waiting_time == self.current_process.burst_time - self.current_process.remaining_time:
                            print(f"\n{self.YELLOW}{self.current_process} has been preempted and moved to a waiting queue.{self.RESET}", end='')
                            self.waiting_queue[self.current_process] = self.current_process.end_waiting_time
                            self.current_process = None

                if self.ready_queue:
                    # sorts processes in ready queue according to arrival time if scheduling algorithm is FCFS
                    if scheduling_algorithm == "FCFS":
                        self.ready_queue = sorted(self.ready_queue, key=lambda process: process.arrival_time)
                    # sorts processes in ready queue according to remainig time and then arrival time if scheduling algorithm is SJF or SRTF
                    elif scheduling_algorithm == "SJF" or scheduling_algorithm == "SRTF":
                        self.ready_queue = sorted(self.ready_queue, key=lambda process: (process.remaining_time, process.arrival_time))
                        # forcefully preempts a current proces if the first process in the queue have a shorter remaining time (preemptive SJF)
                        if scheduling_algorithm == "SRTF" and self.current_process:
                            if not self.current_process:
                                pass
                            elif self.ready_queue[0].remaining_time < self.current_process.remaining_time:
                                print(f"\n{self.YELLOW}{self.current_process} had been preempted and added to the ready queue.{self.RESET}", end='')
                                self.ready_queue.append(self.current_process)
                                self.current_process = None
                    # sorts processes in ready queue according to priority and then arrival time if scheduling algorithm is PJF or PFJ_P
                    elif scheduling_algorithm == "PJF" or scheduling_algorithm == "PJF_P":
                        self.ready_queue = sorted(self.ready_queue, key=lambda process: (process.priority, process.arrival_time))
                        # forcefully preempts a current proces if the first process in the queue have a higher priority
                        if scheduling_algorithm == "PJF_P":
                            if not self.current_process:
                                pass
                            elif self.ready_queue[0].priority < self.current_process.priority:
                                print(
                                    f"\n{self.YELLOW}{self.current_process} had been preempted and added to the ready queue.{self.RESET}",
                                    end='')
                                self.ready_queue.append(self.current_process)
                                self.current_process = None


                    if not self.current_process:
                        """
                        Take the first process in the queue and give it access to the cpu and remove it from the ready queue
                        """
                        print(f"\n{self.GREEN}{self.ready_queue[0]} have started and left the ready queue at {self.current_second}{self.RESET}", end='')
                        self.current_process = self.ready_queue[0]
                        self.ready_queue = self.ready_queue[1:]
                # sets the previous second to the current second
                self.previous_second = self.current_second

class Ui:
    def __init__(self, cpu_scheduler):
        """
        Initiate ui elements and other variables
        generate the ui
        """
        self.ui = Tk()
        self.ui.geometry("500x500")
        # title is the name of the currently specified scheduling algorithm
        self.ui.title(cpu_scheduler.scheduling_algorithm)
        # the id of the next entered process
        # an alert label in read incase user inputs something forbidden
        self.next_process_id = 1
        self.alert_label = Label(self.ui, text="", fg="red")
        # the cpu scheduler object
        self.cpu_scheduler = cpu_scheduler
        # call generate ui function
        self.generate_ui()

    def generate_ui(self):
        # clear old ui
        self.clear_window()

        label = Label(self.ui, text="Add New Process:")
        label.pack()
        # space to enter arrival time
        process_arrival_time_label = Label(self.ui, text="Process Arrival Time")
        process_arrival_time_label.pack()
        process_arrival_time = Entry(self.ui)
        process_arrival_time.pack()
        # space to enter burst time
        process_burst_time_label = Label(self.ui, text="Process Burst Time")
        process_burst_time_label.pack()
        process_burst_time = Entry(self.ui)
        process_burst_time.pack()
        # space to enter process priority
        process_priority_label = Label(self.ui, text="Process priority")
        process_priority_label.pack()
        process_priority = Entry(self.ui)
        process_priority.pack()
        # space to enter the start waiting time
        process_start_waiting_time_label = Label(self.ui, text="After how many second of running will the process ask an input?")
        process_start_waiting_time_label.pack()
        process_start_waiting_time = Entry(self.ui)
        process_start_waiting_time.pack()
        # space to enter the end waiting time
        process_end_waiting_time_label = Label(self.ui, text="After how many seconds of waiting for an input will the process go back to ready queue?")
        process_end_waiting_time_label.pack()
        process_end_waiting_time = Entry(self.ui)
        process_end_waiting_time.pack()

        # submit those variables to a function that will check values validity and then either present an error or create a process object
        submit_button = Button(
            self.ui, text="Submit", command=lambda:
            self.check_and_submit(
                self.next_process_id,
                process_arrival_time.get(),
                process_burst_time.get(),
                process_priority.get(),
                process_start_waiting_time.get(),
                process_end_waiting_time.get()
            )
        )
        submit_button.pack()

        # button to pause and resume timer
        start_pause_cpu_scheduler_timer = Button(self.ui, text="Start/pause scheduling timer", command=lambda: (self.cpu_scheduler.start_pause_cpu_scheduler_timer()))
        start_pause_cpu_scheduler_timer.pack()

    def check_and_submit(self, process_id, arrival_time, burst_time, priority, start_waiting_time, end_waiting_time):

        # throw an error if arrival or burst time are empty
        if arrival_time == "" or burst_time == "":
            self.generate_ui()
            self.alert("Arrival time and burst time cannot be empty.")
        # throw an error if priority is empty and cpu scheduling algorithm is either PJF or PJF_P
        if priority == "":
            if self.cpu_scheduler.scheduling_algorithm == "PJF" or self.cpu_scheduler.scheduling_algorithm == "PJF_P":
                self.generate_ui()
                self.alert("Priority cannot be empty when scheduling algorithm is PJF or PFJ_P.")
            else:
                priority = None
        # throws an error if both start waiting time and end waiting time are empty or either one of them
        if start_waiting_time == "" and end_waiting_time != "":
            self.generate_ui()
            self.alert("Cannot have a start waiting time without an end waiting time.")
        if start_waiting_time != "" and end_waiting_time == "":
            self.generate_ui()
            self.alert("Cannot have an end waiting time without a start waiting time.")
        if end_waiting_time != "" and start_waiting_time == "":
            end_waiting_time = None
            start_waiting_time = None

        # if the start waiting time is greater than or equal the burst time then throw error
        # because the process will have ended by the time start_waiting_time arrives
        if start_waiting_time >= burst_time:
            self.generate_ui()
            self.alert("Process cannot be added to a waiting queue when it have already been completed previously.")

        # convert strings into integers
        process_id =int(process_id)
        arrival_time = int(arrival_time)
        burst_time = int(burst_time)
        # throws error if values are negative
        if arrival_time < 0 or burst_time < 0:
            self.generate_ui()
            self.alert("arrival and burst time cannot be negative.")

        # throw and error if values are smaller than or equal to zero
        if priority:
            priority = int(priority)
            if priority <= 0:
                self.generate_ui()
                self.alert("priority cannot be smaller than or equal zero")

        if start_waiting_time:
            start_waiting_time = int(start_waiting_time)
            if start_waiting_time < 0:
                self.generate_ui()
                self.alert("start waiting time cannot be negative")

        if end_waiting_time:
            end_waiting_time = int(end_waiting_time)
            if end_waiting_time <= 0:
                self.generate_ui()
                self.alert("end waiting time cannot be zero or below")

        # create a process object and adds it to the job queue in the cpu scheduler
        self.cpu_scheduler.add_process(
            Process(
                process_id,
                arrival_time,
                burst_time,
                priority,
                start_waiting_time,
                end_waiting_time
            )
        )
        # sets the id for the next process
        self.next_process_id += 1
        # generate the ui again after completion
        self.generate_ui()

    def alert(self, alert):
        """
        dispalys an error message when called
        """
        if self.alert_label:
            self.alert_label.destroy()
        self.alert_label = Label(self.ui, text=alert, fg="red")
        self.alert_label.pack()

    def clear_window(self):
        """
        clears old ui elements
        """
        for widget in self.ui.winfo_children():
            widget.destroy()

    def start(self):
        """
        start the ui loop
        """
        self.ui.mainloop()

if __name__=="__main__":
    #!!!very important!!!
    # Enter one of those sorting algorithms here (case-sensitive):
    # FCFS(first come first server)
    # SJF(shortest job first(non-preemptive))
    # SRTF(shortest job first(preemptive))
    # PJF(priority job first)
    # PJF_P(priority job first(preemptive))
    scheduling_algorithm = "PJF_P"

    print(scheduling_algorithm)

    # initiate a cpu scheduler object
    cpu_scheduler = CpuScheduler(scheduling_algorithm)

    # initiate a ui object
    ui = Ui(cpu_scheduler)
    # starting the ui loop
    ui.start()