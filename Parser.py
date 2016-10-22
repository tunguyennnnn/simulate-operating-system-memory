import re
import time
from threading import Thread, Semaphore
import random

class ProcessManager:
    def __init__(self, memory):
        self.access_time = 0.7
        self.memory = memory
        self.memory.start()
        self.clock = 1.0

    def get_expressions(self, input_file):
        expressions = open(input_file).read().split("\n")
        self.expressions = [parse(expression) for expression in expressions]



    def get_processes(self, input_file):
        processes = open(input_file).read().split("\n")
        self.number_of_processes = int(processes.pop(0))
        self.processes = []
        i = 0
        while (i < self.number_of_processes):
            groups = re.split("\s+", processes[i])
            process = Process(str(i+1), float(groups[0]),float(groups[1]))
            process.add_semaphore_and_memory(Semaphore(0), self.memory)
            self.processes.append(process)
            i += 1
        self.processes.sort(key=lambda process: process.start_time)

    def execute(self):
        executing_processes = []
        start = time.time()
        while len(self.expressions) > 0 and (len(self.processes) > 0 or len(executing_processes) > 0):
            if len(self.processes) > 0 and ((time.time() - start) + self.clock) >= self.processes[0].start_time:
                current_time = time.time() - start + self.clock           
                while len(self.processes) > 0 and current_time>= self.processes[0].start_time:
                    new_process = self.processes.pop(0)
                    write_to_output_file("Clock: " + str(float(int(current_time))) + ",Process " + new_process.name + ": Started \n")
                    new_process.start()
                    executing_processes.append(new_process)
            if len(executing_processes) > 0 and not self.processExecuting(executing_processes) and not self.memory.isExecuting():
                process = executing_processes.pop(0)
                random_time = random.random() 
                if process.isAssignable(time.time() - start + self.clock + random_time):
                    process.add_expression(self.expressions.pop(0), time.time() - start + self.clock, random_time)
                    process.release()
                executing_processes.append(process)
            executing_processes = self.remove_finished_processes(executing_processes, time.time() - start + self.clock )

        while (len(executing_processes) > 0):
            executing_processes = self.remove_finished_processes(executing_processes, time.time() - start + self.clock)
        self.memory.kill()



    def processExecuting(self, processes):
        for process in processes:
            if process.is_executing():
                return True
        return False

    def kill_all_processes(self, processes):
        for process in processes:
            process.kill()

    def remove_finished_processes(self,processes, time):
        remain_processes = []
        for process in processes:
            if process.isFinished(time):
                write_to_output_file("Clock: " + str(float(int(time))) +", Process " + process.name + ": Finished\n")
                process.kill()
            else: remain_processes.append(process)
        return remain_processes




class Process(Thread):
    def __init__(self, name, start_time, duration):
        super(Process, self).__init__()
        self.name = name
        self.start_time = start_time
        self.duration = duration
        self.assigned = self.done = False

    def add_semaphore_and_memory(self, semaphore, memory):
        self.semaphore = semaphore
        self.memory = memory

    def isAssignable(self, time):
        return self.duration + self.start_time > time and not self.assigned

    def isFinished(self, time):
        return (self.start_time + self.duration) <= time

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
            self.semaphore.acquire()
            if self.done: break
            self.expression.eval(self.memory, self.time, self.name)
            start = time.time()
            while (time.time() - start) < self.executing_time:
                pass
            self.assigned = False




class MemoryManager(Thread):
    def __init__(self):
        super(MemoryManager, self).__init__()
        self.main_memory = MainMemory()
        self.disk_memory = DiskMemory()
        self.done = False
        self.executing = False
        self.add_page_number_to_main_memory("memconfig.txt")

    def add_page_number_to_main_memory(self, input_file):
        page_number = int(open(input_file).read().split("\n")[0])
        self.main_memory.add_page_number(page_number)


    def store(self, variableId, time, process_name, value):
        file = open("output.txt", "a")
        file.write("Clock: " + str(time) + ", Process " + process_name + ", Store Variable " + variableId + ", Value: " + value +"\n")
        file.close()
        if not self.main_memory.store(variableId, value, time):
            self.disk_memory.store(variableId, value)

    def release(self, variableId, time, process_name, value=None):
        file = open("output.txt", "a")
        file.write("Clock: " + str(time) + ", Process " + process_name + ", Release Variable " + variableId +"\n")
        file.close()
        if not self.main_memory.release(variableId):
            self.disk_memory.release(variableId)

    def lookup(self, variableId, timing, process_name, value="None"):
        start = time.time()
        value = self.main_memory.lookup(variableId, timing)
        if value:        
            write_to_output_file("Clock: " + str(timing) + ", Process " + process_name + ", Look up Variable " + variableId + ", Value: " + value + "\n") 
        else:
            if self.disk_memory.lookup(variableId):
                key, value = self.main_memory.remove_least_recent(timing)
                new_key, value = self.disk_memory.swap(variableId, key, value)
                write_to_output_file("Clock: " + str(timing) + " Memory Manager, Swap " + "Variable " + variableId + " with " + key + "\n")
                self.main_memory.store(new_key, value, timing)
                timing = timing + time.time() - start
                write_to_output_file("Clock: " + str(timing) + ", Process " + process_name + ", Look up Variable " + variableId + ", Value: " + value + "\n")
            else:
                write_to_output_file("Clock: " + str(timing) + ", Process " + process_name + ", Look up Variable " + variableId + ", Value: " + "-1\n")
                

    def add_semaphore(self, semaphore):
        self.semaphore = semaphore

    def release_semaphore(self):
        self.semaphore.release()

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
            self.semaphore.acquire()
            if self.done: break
            start = time.time()
            eval("self."+ self.task_type +"(self.variableId, self.time, self.process_name, self.value)")
            self.executing = False




class DiskMemory:
    VM_NAME = "vm.txt"
    def __init__(self):
        open(self.VM_NAME, "w").close()


    def store(self, variableId, value):
        file = open(self.VM_NAME, "a")
        file.write(variableId + " : " + value+ "\n")
        file.close()

    def release(self, variableId):
        file = open(self.VM_NAME, "r")
        storage = file.read().split("\n")
        file.close()
        i = 0
        while i < len(storage):
            if storage[i].split(" : ")[0] == variableId:
                storage.pop(i)
                file = open(self.VM_NAME, "w")
                file.write("\n".join(storage))
                file.close()
                return True
            i += 1
        return False

    def lookup(self, variableId):
        file = open(self.VM_NAME, "r")
        storage = file.read()
        if storage == "":
            return False
        storage.split("\n")
        for line in storage:
            if line.split(" : ")[0] == variableId:
                return True
        return False
    def swap(self,outId, inId, value):
        file = open(self.VM_NAME, "r")
        storage = file.read().split("\n")
        file.close()
        i = 0
        while i < len(storage):
            if storage[i].split(" : ")[0] == outId:
                break
            i += 1
        out_value = storage[i].split(" : ")[1]
        storage[i] = (inId + " : " + value)
        file = open(self.VM_NAME, "w")
        file.write("\n".join(storage))
        file.close()
        return outId, out_value




class MainMemory:
    def __init__(self):
        self.memory = {}
        self.time_stamp = {}

    def add_page_number(self, page_num):
        self.page_number = page_num

    def isFull(self):
        return len(self.memory) == self.page_number

    def store(self, variableId, value, time):
        if self.isFull():
            return False
        self.memory[variableId] = value
        self.time_stamp[variableId] = time
        return True

    def release(self, variableId):
        if self.memory.has_key(variableId):
            del self.memory[variableId]
            del self.time_stamp[variableId]
            return True
        return False

    def lookup(self, variableId, time):
        if self.memory.has_key(variableId):
            self.time_stamp[variableId] = time
            return self.memory[variableId]
        return False

    def remove_least_recent(self, time):
        least_recent_time = time
        least_recent_key = ""
        for key in self.time_stamp:
            if self.time_stamp[key] < least_recent_time:
                least_recent_time = self.time_stamp[key]
                least_recent_key = key
        del self.time_stamp[least_recent_key]
        value = self.memory[least_recent_key]
        del self.memory[least_recent_key]
        return least_recent_key, value



def parse(expression):
    return eval(expression.split(" ")[0] + "Expression(expression)")
    

class Expression():
    def __init__(self, legal_expression, expression):
        if legal_expression.search(expression) == None:
            raise Exception("illegal syntax")

class StoreExpression(Expression):
    def __init__(self, expression):
        legal_expression = re.compile(r"Store(\s\d+){2}$")
        Expression.__init__(self, legal_expression, expression)
        groups = expression.split(" ")
        self.variableId = groups[1]
        self.value = groups[2]

    def eval(self, memory, time, process_name):
        memory.execute_task("store", self.variableId, time, process_name, self.value)


class LookupExpression(Expression):
    def __init__(self, expression):
        legal_expression = re.compile(r"Lookup\s\d+$")
        Expression.__init__(self, legal_expression, expression)
        groups = expression.split(" ")
        self.variableId = groups[1]

    def eval(self, memory, time, process_name):
        memory.execute_task("lookup", self.variableId, time, process_name)

class ReleaseExpression(Expression):
    def __init__(self, expression):
        legal_expression = re.compile(r"Release(\s\d+)$")
        Expression.__init__(self, legal_expression, expression)
        groups = expression.split(" ")
        self.variableId = groups[1]

    def eval(self, memory, time, process_name):
        memory.execute_task("release",self.variableId, time, process_name)



def write_to_output_file(output):
    file = open("output.txt", "a")
    file.write(output)
    file.close()
    print output


memory = MemoryManager()
memory.add_semaphore(Semaphore(0))

manager = ProcessManager(memory)
manager.get_expressions("commands.txt")
manager.get_processes("processes.txt")
manager.execute()
