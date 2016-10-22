from MemoryManager import *
from ProcessManager import *



def main():
    file = open("output.txt", "w")
    file.close()
    memory = MemoryManager()
    memory.add_semaphore(Semaphore(0))
    manager = ProcessManager(memory)
    manager.get_expressions("commands.txt")
    manager.get_processes("processes.txt")
    manager.execute()

if (__name__ == '__main__'):
    main()
