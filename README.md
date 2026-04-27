# CPU Scheduling Algorithms Simulator

Video demo: https://youtu.be/gttFN7C-AtU
## Overview
This program simulates modern CPU scheduling algorithms, 
process allocation, and task execution. 

## Tools & Technologies
- Python 3.12
- Threading library
- Tkinter library

## Features
- Support for several scheduling algorithms, including:
  - First-Come First Served
  - Shortest Job First (preemptive & nonpreemptive)
  - Priority Job First (preemptive & nonpreemptive)
- Job, waiting, and ready queues. 
- GUI for creating processes and controlling the simulator.
- Real-Time process allocation and task execution tracking in the terminal.
- Algorithm evaluation based on the average process completion time.


## Prerequisites
- Python 3.12

## How to run
1. Open a terminal in the directory of choice and run `git clone https://github.com/Abdullahmohammadaref/cpu_scheduling_algorithms`.
2. Open the simulator code with an IDE and navigate to line 372 to change the `scheduling_algorithm` variable value to one of the supported algorithms:
    - `FCFS`(first-come first served)
    - `SJF`(shortest job first(non-preemptive))
    - `SRTF`(shortest job first(preemptive))
    - `PJF`(priority job first)
    - `PJF_P`(priority job first(preemptive))
3. Run the script to start the simulation.
