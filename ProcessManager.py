from Process import *
from MemoryManager import *
from Expression import *
from Write import *
import random


'''
Class ProcessManager:
    - manage process threads by assigning expressions 
'''
class ProcessManager:
    def __init__(self, memory):
        self.memory = memory
        self.memory.start()
        self.clock = 1.0

    
    #get expression from input file
    def get_expressions(self, input_file):
        expressions = open(input_file).read().split("\n")
        self.expressions = [parse(expression) for expression in expressions]


    # get processes from input file
    def get_processes(self, input_file):
        processes = open(input_file).read().split("\n")
        self.number_of_processes = int(processes.pop(0)) #get number of process
        self.processes = []
        i = 0 
        while (i < self.number_of_processes): # for each process,start time and duration time and sempahore
            groups = re.split("\s+", processes[i])
            process = Process(str(i+1), float(groups[0]),float(groups[1]))
            process.add_semaphore_and_memory(Semaphore(0), self.memory)
            self.processes.append(process)
            i += 1
        self.processes.sort(key=lambda process: process.start_time) #sort processes based on start time

    
    #executing processes: 
    def execute(self):
        executing_processes = [] #process queue
        start = time.time() 
        while len(self.expressions) > 0 and (len(self.processes) > 0 or len(executing_processes) > 0): #condition: there is command to execute and processes to execute the command
            if len(self.processes) > 0 and ((time.time() - start) + self.clock) >= self.processes[0].start_time: #if a process is available: 
                current_time = time.time() - start + self.clock           
                while len(self.processes) > 0 and current_time>= self.processes[0].start_time: #put available processes into input queue
                    new_process = self.processes.pop(0)
                    write_to_output_file("Clock: " + str(float(int(current_time))) + ",Process " + new_process.name + ": Started \n")
                    new_process.start()
                    executing_processes.insert(-1, new_process) #insert the new process at the end of the process queue.
                    
            if len(executing_processes) > 0 and not self.processExecuting(executing_processes) and not self.memory.isExecuting(): #ensure mutual exclusion between threads
                process = executing_processes.pop(0) # pop out the first process
                random_time = random.random() # time to perform the command
                if process.isAssignable(time.time() - start + self.clock + random_time): #if the process can run
                    process.add_expression(self.expressions.pop(0), time.time() - start + self.clock, random_time)
                    process.release()
                    executing_processes.append(process)
                else:
                    executing_processes.insert(0, process)
            executing_processes = self.remove_finished_processes(executing_processes, time.time() - start + self.clock ) #remove the processes that are done

        # kill all threads
        while (len(executing_processes) > 0):
            executing_processes = self.remove_finished_processes(executing_processes, time.time() - start + self.clock)
        self.memory.kill()



    # check if one of the process is executing
    def processExecuting(self, processes):
        for process in processes:
            if process.is_executing():
                return True
        return False

    def kill_all_processes(self, processes):
        for process in processes:
            process.kill()

    # remove processes that have been done based on clock time
    def remove_finished_processes(self,processes, time):
        remain_processes = []
        for process in processes:
            if process.isFinished(time):
                write_to_output_file("Clock: " + str(float(int(time))) +", Process " + process.name + ": Finished\n")
                process.kill()
            else: remain_processes.append(process)
        return remain_processes


