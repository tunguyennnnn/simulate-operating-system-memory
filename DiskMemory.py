class DiskMemory:
    VM_NAME = "vm.txt"
    def __init__(self):
        open(self.VM_NAME, "w").close()
    #store vairable to file
    def store(self, variableId, value):
        file = open(self.VM_NAME, "a")
        file.write(variableId + " : " + value+ "\n")
        file.close()

    # delete variable if it exists, otherwise return false
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

    #replace the variable with a new one
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


