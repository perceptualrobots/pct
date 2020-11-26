# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/07_errors.ipynb (unless otherwise specified).

__all__ = ['BaseErrorCollector', 'TotalError']

# Cell
import random
import numpy as np
import math
import networkx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from deap import algorithms
from abc import ABC, abstractmethod
from deap import base
from deap import creator
from deap import tools
from deap.tools import History
from .putils import sigmoid

# Cell
class BaseErrorCollector(ABC):
    "Base class of an error collector. This class is not used direclty by developers, but defines the interface common to all."
    def __init__(self):
        self.error_value=0

    def error(self):
        return self.error_value

    def add_error_data(self, data=[]):
        for datum in data:
            print(datum)
            self.error_value+=datum


    #@abstractmethod


# Cell
class TotalError(BaseErrorCollector):
    "A class to collect all the errors of the control system run."
    'Parameters:'
    'x - the initial limit of the range for an individual'

    def __init__(self, **cargs):
        super().__init__()


