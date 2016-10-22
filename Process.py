from threading import Thread, Semaphore
import time
from Write import *

'''
Class Process: inherit from theading class
'''
class Process(Thread):
    def __init__(self, name, start_time, duration):
        super(Process, self).__init__()
        self.name = name
        self.start_time = start_time
        self.duration = duration
        self.assigned = self.done = False

    
    # add semaphore and memory manager 
    def add_semaphore_and_memory(self, semaphore, memory):
        self.semaphore = semaphore
        self.memory = memory

    # check if a process can be given a command based on clock time and its duration
    def isAssignable(self, time):
        return self.duration + self.start_time > time and not self.assigned
    
    # check if a process is finished base on clock time and its duration
    def isFinished(self, time):
        return (self.start_time + self.duration) <= time

    # add command to execute 
    def add_expression(self, expression, time, executing_time):
        self.executing_time = executing_time
        self.expression = expression
        self.time = time
        self.assigned = True

    def is_executing(self):
        return self.assigned

    def release(self):
        self.semaphore.release()

    def kill(self):
        self.semaphore.release()
        self.done = True

    
    def run(self):
        while True:
            self.semaphore.acquire() # lock the process from executing
            if self.done: break
            self.expression.eval(self.memory, self.time, self.name)
            start = time.time()
            while (time.time() - start) < self.executing_time: #execute for a random time
                pass
            self.assigned = False

