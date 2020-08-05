# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_functions.ipynb (unless otherwise specified).

__all__ = ['BaseFunction', 'Proportional', 'Integration']

# Cell
from abc import ABC, abstractmethod

# Cell
class BaseFunction(ABC):
    "Base class of a PCT function."
    def __init__(self):
        self.output = 0

    @abstractmethod
    def __call__(self):
        pass

    def set_output(self, output):
        self.output= output

    def get_output(self):
        return self.output

# Cell
class Proportional(BaseFunction):
    "Proportional function."
    def __init__(self, gain):
        super().__init__()
        self.gain = gain

    def __call__(self, input):
        self.output = input * self.gain
        return self.output

# Cell
class Integration(BaseFunction):
    "Integration function."
    def __init__(self, gain, slow):
        super().__init__()
        self.gain = gain
        self.slow = slow

    def __call__(self, input):
        self.output = self.output +  ((input * self.gain) - self.output)/self.slow
        return self.output
