# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_functions.ipynb (unless otherwise specified).

__all__ = ['BaseFunction', 'Proportional', 'Variable', 'GreaterThan', 'Subtract', 'Constant', 'Integration',
           'WeightedSum', 'IndexedParameter', 'OpenAIGym']

# Cell
import numpy as np
import gym
from abc import ABC, abstractmethod
from .utilities import UniqueNamer
from .utilities import FunctionsList

# Cell
class BaseFunction(ABC):
    "Base class of a PCT function. This class is not used direclty by developers, but defines the functionality common to all."
    def __init__(self, name, value, links=None, new_name=True):
        self.value = value
        self.links = []
        self.handle_links(links)


        #print(f'size {len(UniqueNamer.getInstance().names)} {name} {name in UniqueNamer.getInstance().names}', end=" ")
        if new_name:
            self.name = UniqueNamer.getInstance().get_name(name)
        else:
            self.name = name
        #print(self.name)
        FunctionsList.getInstance().add_function(self)
        self.decimal_places = 3

    @abstractmethod
    def __call__(self, verbose=False):
        if verbose :
            print(self.output_string(), end= " ")

        return self.value
    def handle_links(self, links):
        if links!=None:
            if isinstance(links, dict):
                if len(links)>0:
                    for key in links.keys():
                        self.links.append(FunctionsList.getInstance().get_function(links[key]))
                    return

            if isinstance(links, list):
                for link in links:
                    self.links.append(link)
                    #if isinstance(link, dic):
                    #    self.links.append(FunctionsList.getInstance().get_function(link))
                    #else:
            #else:

                #if isinstance(links, str):
                 #   self.links.append(FunctionsList.getInstance().get_function(links))
                #else:
                 #   self.links.append(links)




    def output_string(self):
        return f'{round(self.value, self.decimal_places):.{self.decimal_places}f}'

    def check_links(self, num):
        if len(self.links) != num:
            raise Exception(f'Incorrect number of links {len(self.links)} for function {self.name}. {num} expected.')

    def set_decimal_places(self, dp):
        self.decimal_places = dp

    @abstractmethod
    def summary(self, str):
        print(f'{self.name} {type(self).__name__}', end = " ")
        if len(str)>0:
            print(f'| {str}', end= " ")
        print(f'| {self.value}', end = " ")
        if len(self.links)>0:
            print('| links ', end=" ")
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

    def get_indexed_value(self, index):
        return self.value[index]

    def add_link(self, linkfn):
        self.links.append(linkfn)

    def close(self):
        pass

    @classmethod
    def from_config(cls,  config):
        #print("a:",config)
        func = cls(new_name=False, **config)
        #key  = 'links'
        #if key in config:
        #    for key in config['links'].keys():
        #        func.links.append(FunctionsList.getInstance().get_function(config['links'][key]))

        #print("b:",func.get_config())
        return func

    def __str__(self):
        return str(self.__dict__)

# Cell
class Proportional(BaseFunction):
    "A proportion of the input value as defined by the gain parameter. Parameters: The gain value. Links: One."
    def __init__(self, gain=1, value=0, name="proportional", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
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
    def __init__(self,  value=0, name="variable", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)

    def __call__(self, verbose=False):
        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()
        return config



# Cell
class GreaterThan(BaseFunction):
    "One of two supplied values is returned if the input is greater than supplied threshold.</br> Parameters: The threshold and upper and lower value. Links: One"
    def __init__(self, threshold=0, upper=1, lower=0, value=0, name="greaterthan", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
        self.threshold=threshold
        self.upper=upper
        self.lower=lower

    def __call__(self, verbose=False):
        input = self.links[0].get_value()
        if input >= self.threshold:
            self.value = self.upper
        else:
            self.value = self.lower

        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()
        return config



# Cell
class Subtract(BaseFunction):
    "A function that subtracts one value from another. Parameter: None. Links: Two links required to each the values to be subtracted."
    def __init__(self, value=0, name="subtract", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)

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
    def __init__(self, value=0, name="constant", new_name=True, **cargs):
        super().__init__(name, value, None, new_name)

    def __call__(self, verbose=False):
        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        return super().get_config()


# Cell
class Integration(BaseFunction):
    "A leaky integrating function. Equivalent of a exponential smoothing function, of the amplified input. Parameter: The gain and slow values. Links: One."
    def __init__(self, gain=1, slow=2, value=0, name="integration", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
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
    "A function that combines a set of inputs by multiplying each by a weight and then adding them up. Parameter: The weights array. Links: Links to all the input functions."
    def __init__(self, weights=np.ones(3), value=0, name="weighted_sum", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
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

# Cell
class IndexedParameter(BaseFunction):
    "A function that returns a parameter from a linked function, indexed by number. Parameter: The index. Links: One."
    def __init__(self, index=None, value=0, name="indexed_parameter", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
        self.index = index

    def __call__(self, verbose=False):
        super().check_links(1)
        self.value = self.links[0].get_indexed_value(self.index)

        return super().__call__(verbose)

    def summary(self):
        super().summary(f'index {self.index}')


    def get_config(self):
        config = super().get_config()
        config["index"] = self.index
        return config

# Cell
class OpenAIGym(BaseFunction):
    "A function that creates an runs an environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    def __init__(self, env_name=None, render=False, video_wrap=False, value=0, name="gym", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)

        self.video_wrap = video_wrap
        self.create_env(env_name, 4000)
        self.render = render
        self.reward = 0
        self.done = False
        self.info = {}

    def __call__(self, verbose=False):
        super().check_links(1)
        input = self.links[0].get_value()
        if input == 1 or input == -1 or input == 0:
            obs = self.env.step(input)
        else:
            raise Exception(f'OpenAIGym: Input value of {input} is not valid, must be 1,0 or -1.')

        self.value = obs[0]

        self.reward = obs[1]
        self.done = obs[2]
        self.info = obs[3]

        if self.render:
            self.env.render()

        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()
        config["values"] = self.value
        config["reward"] = self.reward
        config["done"] = self.done
        config["info"] = self.info

        return config

    def create_env(self, env_name, max_episode_steps):
        genv = gym.make(env_name)
        genv._max_episode_steps = max_episode_steps
        if self.video_wrap:
            self.env =  vid.wrap_env(genv)
        else:
            self.env = genv
            self.env.reset()

    def close(self):
        self.env.close()
