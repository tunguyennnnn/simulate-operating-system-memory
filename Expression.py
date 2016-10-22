    
import re

# function to parse an expression
def parse(expression):
    return eval(expression.split(" ")[0] + "Expression(expression)")


# Abstract class to initialize an expression and check syntax
class Expression():
    def __init__(self, legal_expression, expression):
        if legal_expression.search(expression) == None:
            raise Exception("illegal syntax")

        
'''
 StoreExpression class to store variable and value to memory
'''
class StoreExpression(Expression):
    def __init__(self, expression):
        legal_expression = re.compile(r"Store(\s\d+){2}$")
        Expression.__init__(self, legal_expression, expression)
        groups = expression.split(" ")
        self.variableId = groups[1]
        self.value = groups[2]
    #interpret the expression by passing parameteres to memory manager
    def eval(self, memory, time, process_name):
        memory.execute_task("store", self.variableId, time, process_name, self.value)


'''
    LookupExpression:  
'''

class LookupExpression(Expression):
    def __init__(self, expression):
        legal_expression = re.compile(r"Lookup\s\d+$")
        Expression.__init__(self, legal_expression, expression)
        groups = expression.split(" ")
        self.variableId = groups[1]

    def eval(self, memory, time, process_name):
        memory.execute_task("lookup", self.variableId, time, process_name)

'''
    Release Expression:
'''
class ReleaseExpression(Expression):
    def __init__(self, expression):
        legal_expression = re.compile(r"Release(\s\d+)$")
        Expression.__init__(self, legal_expression, expression)
        groups = expression.split(" ")
        self.variableId = groups[1]

    def eval(self, memory, time, process_name):
        memory.execute_task("release",self.variableId, time, process_name)

