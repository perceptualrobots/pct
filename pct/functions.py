# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_functions.ipynb (unless otherwise specified).

__all__ = ['UniqueNamer', 'FunctionsList', 'BaseFunction', 'Proportional', 'Variable', 'Subtract', 'Constant',
           'Integration', 'WeightedSum']

# Cell
import numpy as np
from abc import ABC, abstractmethod

# Cell
class UniqueNamer:
    __instance = None
    @staticmethod
    def getInstance():
      """ Static access method. """
      if UniqueNamer.__instance == None:
         UniqueNamer()
      return UniqueNamer.__instance
    def __init__(self):
      """ Virtually private constructor. """
      if UniqueNamer.__instance != None:
         raise Exception("This class is a singleton!")
      else:
         UniqueNamer.__instance = self
      self.names = {}

    def clear(self):
      self.names = {}

    def get_name(self, name):
        if name in self.names.keys():
            num = self.names[name]+1
            self.names[name]=num
            name = f'{name}{num}'
        else:
            self.names[name]=0
        return name

# Cell
class FunctionsList:
    __instance = None
    @staticmethod
    def getInstance():
      """ Static access method. """
      if FunctionsList.__instance == None:
         FunctionsList()
      return FunctionsList.__instance
    def __init__(self):
      """ Virtually private constructor. """
      if FunctionsList.__instance != None:
         raise Exception("This class is a singleton!")
      else:
         FunctionsList.__instance = self
      self.functions = {}

    def clear(self):
      self.functions = {}


    def add_function(self, func):
        name = func.get_name()
        self.functions[name]=func

        return name

    def get_function(self, name):
        func = self.functions[name]

        return func

# Cell
class BaseFunction(ABC):
    "Base class of a PCT function. This class is not used direclty by developers, but defines the functionality common to all."
    def __init__(self, name, value):
        self.value = value
        self.links = []
        self.name = UniqueNamer.getInstance().get_name(name)
        FunctionsList.getInstance().add_function(self)

    @abstractmethod
    def __call__(self, verbose=False):
        if verbose :
            print(f'{self.value:.3f}', end= " ")

        return self.value

    @abstractmethod
    def summary(self, str):
        print(f'{self.name} {type(self).__name__}', end = " ")
        if len(str)>0:
            print(f'| {str}', end= " ")
        print(f'| {self.value}', end = " ")
        if len(self.links)>0:
            print(f'| links ', end=" ")
        for link in self.links:
            print(link.get_name(), end= " ")
        print()

    @abstractmethod
    def get_config(self):
        config = {"type": type(self).__name__,
                    "name": self.name,
                    "value": self.value}

        ctr=0
        links={}
        for link in self.links:
            links[ctr]=link.get_name()
            ctr+=1

        config['links']=links
        return config

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name=name

    def set_value(self, value):
        self.value= value

    def get_value(self):
        return self.value

    def add_link(self, linkfn):
        self.links.append(linkfn)

    @classmethod
    def from_config(cls, config):
        func = cls(**config)
        key  = 'links'
        if key in config:
            for key in config['links'].keys():
                func.links.append(FunctionsList.getInstance().get_function(config['links'][key]))
        return func


# Cell
class Proportional(BaseFunction):
    "A proportion of the input value as defined by the gain parameter. Parameters: The gain value. Links: One."
    def __init__(self, gain=1, value=0, name="proportional", **cargs):
        super().__init__(name, value)
        self.gain = gain

    def __call__(self, verbose=False):
        input = self.links[0].get_value()
        self.value = input * self.gain
        return super().__call__(verbose)

    def summary(self):
        super().summary(f'gain {self.gain}')

    def get_config(self):
        config = super().get_config()
        config["gain"] = self.gain
        return config

# Cell
class Variable(BaseFunction):
    "A function that returns a variable value. Parameter: The variable value. Links: None"
    def __init__(self,  value=0, name="variable", **cargs):
        super().__init__(name, value)

    def __call__(self, verbose=False):
        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()
        return config



# Cell
class Subtract(BaseFunction):
    "A function that subtracts one value from another. Parameter: None. Links: Two links required to each the values to be subtracted."
    def __init__(self, value=0, name="subtract", **cargs):
        super().__init__(name, value)

    def __call__(self, verbose=False):
        #print("Sub ", self.links[0].get_value(),self.links[1].get_value() )
        self.value = self.links[0].get_value()-self.links[1].get_value()

        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        return super().get_config()


# Cell
class Constant(BaseFunction):
    "A function that returns a constant value. Parameter: The constant value. Links: None"
    def __init__(self, value=0, name="constant", **cargs):
        super().__init__(name, value)

    def __call__(self, verbose=False):
        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        return super().get_config()


# Cell
class Integration(BaseFunction):
    "A leaky integrating function. Equivalent of a exponential smoothing function, of the amplified input. Parameter: The gain and slow values. Links: One."
    def __init__(self, gain=1, slow=2, value=0, name="integration", **cargs):
        super().__init__(name, value)
        self.gain = gain
        self.slow = slow

    def __call__(self, verbose=False):
        input = self.links[0].get_value()
        self.value = self.value +  ((input * self.gain) - self.value)/self.slow

        return super().__call__(verbose)

    def summary(self):
        super().summary(f'gain {self.gain} slow {self.slow} ')

    def get_config(self):
        config = super().get_config()
        config["gain"] = self.gain
        config["slow"] = self.slow
        return config


# Cell
class WeightedSum(BaseFunction):
    "A function that combines a set of inputs by multyplying each by a weight and then adding them up. Parameter: The weights array. Links: Links to all the input functions."
    def __init__(self, value=0, weights=np.ones(3), name="weighted_sum", **cargs):
        super().__init__(name, value)
        self.weights = weights

    def __call__(self, verbose=False):
        if len(self.links) != self.weights.size:
            raise Exception(f'Number of links {len(self.links)} and weights {self.weights.size} must be the same.')

        inputs = np.array([link.get_value() for link in self.links])
        self.value = np.dot(inputs, self.weights)

        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()
        config["weights"] = self.weights
        return config