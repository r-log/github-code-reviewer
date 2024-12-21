# Bad practices example
from random import *
import os
import sys
import json


def Func(x, y):
    z = x+y
    return z


class badClass:
    def __init__(self, val):
        self.VAL = val

    def DoSomething(self):
        try:
            # Too broad exception
            a = 1/0
        except:
            print('error')

        # Magic numbers
        if self.VAL > 42:
            return 'high'
        else:
            return 'low'

# Inconsistent naming


def calculate_SOMETHING(inpt):
    Output = []
    # Nested loops with complex logic
    for i in inpt:
        for j in inpt:
            if i > j:
                if i - j > 10:
                    Output.append(i)
    return Output


# Global variable
GLOBAL_VAR = 100


def process_data():
    global GLOBAL_VAR
    GLOBAL_VAR += 1
