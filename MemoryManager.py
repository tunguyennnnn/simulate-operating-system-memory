from DiskMemory import *
from MainMemory import *
from threading import Thread, Semaphore
from Write import *
import time

'''
Class Memory manager:
    - inherit from threading's Thread class
    - manage main memory and disk memory
'''

class MemoryManager(Thread):
    def __init__(self):
        super(MemoryManager, self).__init__()
        self.main_memory = MainMemory()
        self.disk_memory = DiskMemory()
        self.done = False
        self.executing = False
        self.add_page_number_to_main_memory("memconfig.txt")

    #assign memory page number from input file
    def add_page_number_to_main_memory(self, input_file):
        page_number = int(open(input_file).read().split("\n")[0])
        self.main_memory.add_page_number(page_number)


    #store API: store to main memory if it is not full, otherwise store to disk
    def store(self, variableId, time, process_name, value):
        write_to_output_file("Clock: " + str(time) + ", Process " + process_name + ", Store Variable " + variableId + ", Value: " + value +"\n")
        if not self.main_memory.store(variableId, value, time):
            self.disk_memory.store(variableId, value)

    #Release API: delete in memory first, if variable is no found, delete it in disk
    def release(self, variableId, time, process_name, value=None):
        write_to_output_file("Clock: " + str(time) + ", Process " + process_name + ", Release Variable " + variableId +"\n")
        if not self.main_memory.release(variableId):
            self.disk_memory.release(variableId)

    #Lookup API: perform lookup and swaping if needed
    def lookup(self, variableId, timing, process_name, value=None):
        start = time.time()
        value = self.main_memory.lookup(variableId, timing)
        if value: #if the variable in the main memory:
            write_to_output_file("Clock: " + str(timing) + ", Process " + process_name + ", Look up Variable " + variableId + ", Value: " + value + "\n") 
        else:
            if self.disk_memory.lookup(variableId): # if variable in disk, perform swapping
                key, value = self.main_memory.remove_least_recent(timing)
                new_key, value = self.disk_memory.swap(variableId, key, value)
                write_to_output_file("Clock: " + str(timing) + " Memory Manager, Swap " + "Variable " + variableId + " with " + key + "\n")
                self.main_memory.store(new_key, value, timing)
                timing = timing + time.time() - start
                write_to_output_file("Clock: " + str(timing) + ", Process " + process_name + ", Look up Variable " + variableId + ", Value: " + value + "\n")
            else: #elese return -1
                write_to_output_file("Clock: " + str(timing) + ", Process " + process_name + ", Look up Variable " + variableId + ", Value: " + "-1\n")
                
    #add semaphore to the thread
    def add_semaphore(self, semaphore):
        self.semaphore = semaphore

    def release_semaphore(self):
        self.semaphore.release()

    
    # provide next command to main memory to execute
    def execute_task(self, task_type, variableId, time, process_name, value=None):
        self.task_type = task_type
        self.variableId = variableId
        self.time = time
        self.process_name = process_name
        self.value = value
        self.executing = True
        self.release_semaphore()

    def isExecuting(self):
        return self.executing
    
    def kill(self):
        self.semaphore.release()
        self.done = True
        
    def run(self):
        while True:
            self.semaphore.acquire() # wait to unlock
            if self.done: break
            start = time.time()
            eval("self."+ self.task_type +"(self.variableId, self.time, self.process_name, self.value)") # call one of the api corresponding to the command
            self.executing = False


