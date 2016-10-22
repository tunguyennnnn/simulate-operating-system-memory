
class MainMemory:
    def __init__(self):
        self.memory = {} #hold variable
        self.time_stamp = {} #hold the time stamp of the vairable

    def add_page_number(self, page_num):
        self.page_number = page_num

    def isFull(self):
        return len(self.memory) == self.page_number

    #store: return false if main memory is full
    def store(self, variableId, value, time):
        if self.isFull():
            return False
        self.memory[variableId] = value
        self.time_stamp[variableId] = time
        return True

    #release: return false if vairable is not in the memory
    def release(self, variableId):
        if self.memory.has_key(variableId):
            del self.memory[variableId]
            del self.time_stamp[variableId]
            return True
        return False

    #lookup: return false if variable is not in the memory
    def lookup(self, variableId, time):
        if self.memory.has_key(variableId):
            self.time_stamp[variableId] = time
            return self.memory[variableId]
        return False

    # the method pops the variable that is least recently used base on time_stamp attribute
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

