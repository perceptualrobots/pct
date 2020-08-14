# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_functions.ipynb (unless otherwise specified).

__all__ = ['BaseFunction', 'Proportional', 'Variable', 'Constant', 'Subtract', 'Integration']

# Cell
from abc import ABC, abstractmethod

# Cell
class BaseFunction(ABC):
    "Base class of a PCT function. This class is not used direclty by developers, but defines the functionality common to all."
    def __init__(self, name, value):
        self.value = value
        self.links = []
        self.name = name

    @abstractmethod
    def __call__(self, verbose=False):
        if verbose :
            print(f'{self.value}', end= " ")

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

    #def from_config(cls, config):
    @classmethod
    def from_config(cls, config):
        #cls = config.pop("type")
        return cls(**config)


# Cell
class Proportional(BaseFunction):
    "A proportion of the input value as defined by the gain parameter."
    def __init__(self, gain=1, name="proportional", value=0, **cargs):
        super(Proportional, self).__init__(name, value)
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
    "A function that returns a variable value."
    "Parameter: The variable value."
    "Links: None"
    def __init__(self, variable, name="variable"):
        super().__init__(name)
        self.value = variable

    def __call__(self, verbose=False):
        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()
        return config



# Cell
class Constant(BaseFunction):
    "A function that returns a constant value."
    def __init__(self, constant, value=0, name="constant"):
        super().__init__(name, value)
        self.value = constant

    def __call__(self, verbose=False):
        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()


# Cell
class Subtract(BaseFunction):
    "A function that subtracts one value from another."
    def __init__(self, name="subtract"):
        super().__init__(name)

    def __call__(self, verbose=False):
        #print("Sub ", self.links[0].get_value(),self.links[1].get_value() )
        self.value = self.links[0].get_value()-self.links[1].get_value()

        return super().__call__(verbose)

    def summary(self):
        super().summary("")


# Cell
class Integration(BaseFunction):
    "Integration function."
    def __init__(self, gain, slow, value=0, name="integration"):
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
