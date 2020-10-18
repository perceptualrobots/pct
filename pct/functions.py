# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_functions.ipynb (unless otherwise specified).

__all__ = ['BaseFunction', 'Subtract', 'Proportional', 'Variable', 'PassOn', 'GreaterThan', 'Constant', 'Step',
           'Integration', 'IntegrationDual', 'Sigmoid', 'WeightedSum', 'IndexedParameter', 'OpenAIGym']

# Cell
import numpy as np
import gym
import json
import math
import networkx as nx
from abc import ABC, abstractmethod
from .putils import sigmoid
from .putils import UniqueNamer
from .putils import FunctionsList

# Cell
class BaseFunction(ABC):
    "Base class of a PCT function. This class is not used direclty by developers, but defines the functionality common to all."
    def __init__(self, name, value, links=None, new_name=True):
        self.value = value
        self.links = []
        self.handle_links(links)
        self.checklinks=True

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

    def run(self, steps=None, verbose=False):
        for i in range(steps):
            out = self(verbose)
        return out

    def handle_links(self, links):
        if links!=None:
            if isinstance(links, dict):
                if len(links)>0:
                    for key in links.keys():
                        self.links.append(FunctionsList.getInstance().get_function(links[key]))
                return

            if isinstance(links, list):
                for link in links:
                    if isinstance(link, str):
                        self.links.append(FunctionsList.getInstance().get_function(link))
                    else:
                        self.links.append(link)
                return

            if isinstance(links, str):
                self.links.append(FunctionsList.getInstance().get_function(links))
                return

            self.links.append(links)

    def draw(self, with_labels=True,  font_size=12, font_weight='bold', node_color='red',
             node_size=500, arrowsize=25, align='horizontal', file=None):
        graph = self.graph(layer=0, layer_edges=True)
        pos = nx.multipartite_layout(graph, subset_key="layer", align=align)
        nx.draw(graph,  pos=pos, with_labels=with_labels, font_size=font_size, font_weight=font_weight,
                node_color=node_color,  node_size=node_size, arrowsize=arrowsize)

    def graph(self, layer=None, layer_edges=False):
        graph = nx.DiGraph()

        self.set_graph_data(graph, layer=layer, layer_edges=layer_edges)

        return graph

    def set_graph_data(self, graph, layer=None, layer_edges=False):
        node_name = self.name
        edges = []
        for link in self.links:
            func = FunctionsList.getInstance().get_function(link)
            if isinstance(func, str):
                name = func
            else:
                name = func.get_name()

            if layer_edges:
                graph.add_node(name, layer=layer+1)

            edges.append((name,self.name))

        graph.add_node(node_name, layer=layer)
        graph.add_edges_from( edges)




    def output_string(self):
        if isinstance (self.value, list):
            return [f'{round(item, self.decimal_places):.{self.decimal_places}f}' for item in self.value]

        return f'{round(self.value, self.decimal_places):.{self.decimal_places}f}'

    def check_links(self, num):
        if self.checklinks:
            ctr=0
            for link in self.links:
                func = FunctionsList.getInstance().get_function(link)
                self.links[ctr]=func
                ctr+=1

            if len(self.links) != num:
                raise Exception(f'Incorrect number of links {len(self.links)} for function {self.name}. {num} expected.')

            self.checklinks = False

    def set_decimal_places(self, dp):
        self.decimal_places = dp


    @abstractmethod
    def summary(self, sstr):
        "Print the summary of the function configuration. No argument required."
        print(f'{self.name} {type(self).__name__}', end = " ")
        if len(sstr)>0:
            print(f'| {sstr}', end= " ")
        print(f'| {self.value}', end = " ")
        if len(self.links)>0:
            print('| links ', end=" ")
        for link in self.links:
            func = FunctionsList.getInstance().get_function(link)
            if isinstance(func, type(str)):
                fname = func
            else:
                fname = func.get_name()

            print(fname, end= " ")
        print()

    @abstractmethod
    def get_config(self):
        "Return the JSON  configuration of the function."
        config = {"type": type(self).__name__,
                    "name": self.name}

        if isinstance(self.value, np.ndarray):
            config["value"] = self.value.tolist()
        else:
            config["value"] = self.value

        ctr=0
        links={}
        for link in self.links:
            func = FunctionsList.getInstance().get_function(link)
            try:
                links[ctr]=func.get_name()
            except AttributeError:
                raise Exception(f' there is no function called {link}, ensure it exists first.')
            ctr+=1

        config['links']=links
        return config

    def get_name(self):
        return self.name

    def set_name(self, name):
        FunctionsList.getInstance().remove_function(self.name)
        self.name=name
        FunctionsList.getInstance().add_function(self)

    def set_property(self, property_name, property_value):
        #self[property_name]= property_value
        exec(f'self.{property_name}= {property_value}')

    def set_value(self, value):
        self.value= value

    def get_value(self):
        return self.value

    def get_indexed_value(self, index):
        return self.value[index]

    def add_link(self, linkfn):
        self.links.append(linkfn)

    def set_link(self, linkfn):
        self.links = [linkfn]

    def clear_links(self):
        self.links = []

    def close(self):
        pass

    def save(self, file=None, indent=4):
        jsondict = json.dumps(self.get_config(), indent=indent)
        f = open(file, "w")
        f.write(jsondict)
        f.close()

    @classmethod
    def load(cls, file):
        with open(file) as f:
            config = json.load(f)
        return cls.from_config(config)

    @classmethod
    def from_config(cls,  config):
        func = cls(new_name=False, **config)
        return func

    def __str__(self):
        return str(self.__dict__)

# Cell
class Subtract(BaseFunction):
    "A function that subtracts one value from another. Parameter: None. Links: Two links required to each the values to be subtracted."
    def __init__(self, value=0, name="subtract", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)

    def __call__(self, verbose=False):
        super().check_links(2)
        #print("Sub ", self.links[0].get_value(),self.links[1].get_value() )
        self.value = self.links[0].get_value()-self.links[1].get_value()

        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        return super().get_config()


# Cell
class Proportional(BaseFunction):
    "A proportion of the input value as defined by the gain parameter. Parameters: The gain value. Links: One."
    def __init__(self, gain=1, value=0, name="proportional", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
        self.gain = gain

    def __call__(self, verbose=False):
        super().check_links(1)
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
class PassOn(BaseFunction):
    "A function that passes on a variable value from a linked function. Parameter: None. Links: One"
    def __init__(self,  value=0, name="variable", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)

    def __call__(self, verbose=False):
        super().check_links(1)
        self.value = self.links[0].get_value()
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
        super().check_links(1)
        input = self.links[0].get_value()
        if input >= self.threshold:
            self.value = self.upper
        else:
            self.value = self.lower

        return super().__call__(verbose)

    def summary(self):
        super().summary(f'threshold {self.threshold} upper {self.upper} lower {self.lower} ')

    def get_config(self):
        config = super().get_config()

        config["threshold"] = self.threshold
        config["upper"] = self.upper
        config["lower"] = self.lower
        return config



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
class Step(BaseFunction):
    "A function that returns an alternating signal. Parameter: The upper and lower values, and a delay value. Links: None"
    def __init__(self, upper=None, lower=None, delay=None, period=None, value=0, name="step", new_name=True, **cargs):
        self.ctr=1
        self.upper=upper
        self.lower=lower
        self.delay=delay
        self.period=period
        self.delay_finished=False

        super().__init__(name, value, None, new_name)

    def __call__(self, verbose=False):
        if self.ctr>self.delay-1:
            if not self.delay_finished:
                self.value = self.upper
                self.delay_finished=True
                self.ctr = self.period/2

            if self.ctr % self.period ==0 :
                if self.value != self.lower:
                    self.value = self.lower
                elif self.value != self.upper:
                    self.value = self.upper
                #print(self.ctr, self.value)

        self.ctr += 1
        return super().__call__(verbose)

    def summary(self):
        super().summary(f'upper {self.upper} lower {self.lower} delay {self.delay} period {self.period}')

    def get_config(self):
        config = super().get_config()
        config["upper"] = self.upper
        config["lower"] = self.lower
        config["delay"] = self.delay
        config["period"] = self.period
        return config

# Cell
class Integration(BaseFunction):
    "A leaky integrating function. Equivalent of a exponential smoothing function, of the amplified input. Parameters: The gain and slow values. Links: One."
    def __init__(self, gain=1, slow=2, value=0, name="integration", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
        self.gain = gain
        self.slow = slow

    def __call__(self, verbose=False):
        super().check_links(1)
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
class IntegrationDual(BaseFunction):
    "A leaky integrating function, applying one signal to another. Equivalent of a exponential smoothing function, of the amplified input. Parameters: The gain and slow values. Links: Two."
    def __init__(self, gain=1, slow=2, value=0, name="integration", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
        self.gain = gain
        self.slow = slow

    def __call__(self, verbose=False):
        super().check_links(2)
        input = self.links[0].get_value()
        output = self.links[1].get_value()
        #print(input, output)
        self.value = output +  ((input * self.gain) - output)/self.slow

        return super().__call__(verbose)

    def summary(self):
        super().summary(f'gain {self.gain} slow {self.slow} ')

    def get_config(self):
        config = super().get_config()
        config["gain"] = self.gain
        config["slow"] = self.slow
        return config

# Cell
class Sigmoid(BaseFunction):
    "A sigmoid function. Similar to a proportional function, but kept within a limit (+/- half the range). Parameters: The range and scale (slope) values. Links: One."
    def __init__(self, range=2, scale=2, value=0, name="sigmoid", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
        self.range = range
        self.scale = scale

    def __call__(self, verbose=False):
        super().check_links(1)
        input = self.links[0].get_value()
        self.value = sigmoid(input, self.range, self.scale)

        return super().__call__(verbose)

    def summary(self):
        super().summary(f'range {self.range} scale {self.scale} ')

    def get_config(self):
        config = super().get_config()
        config["range"] = self.range
        config["scale"] = self.scale
        return config

# Cell
class WeightedSum(BaseFunction):
    "A function that combines a set of inputs by multiplying each by a weight and then adding them up. Parameter: The weights array. Links: Links to all the input functions."
    def __init__(self, weights=np.ones(3), value=0, name="weighted_sum", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
        if isinstance(weights, list):
            self.weights = np.array(weights)
        else:
            self.weights = weights

    def __call__(self, verbose=False):
        if len(self.links) != self.weights.size:
            raise Exception(f'Number of links {len(self.links)} and weights {self.weights.size} must be the same.')

        super().check_links(len(self.links))
        inputs = np.array([link.get_value() for link in self.links])
        self.value = np.dot(inputs, self.weights)

        return super().__call__(verbose)

    def summary(self):
        super().summary(f'weights {self.weights}')

    def get_config(self):
        config = super().get_config()
        config["weights"] = self.weights.tolist()
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
        self.env_name=env_name
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

        # from obs[0], indices
        # 1 cart_velocity
        # 0 cart_position
        # 3 pole_velocity
        # 2 pole_angle

        self.value = obs[0]
        if self.name == 'CartPole-v1':
            self.value = np.append(self.value, obs[0]+math.sin(obs[2]))
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
        config["env_name"] = self.env_name
        #config["values"] = self.value
        config["reward"] = self.reward
        config["done"] = self.done
        config["info"] = self.info

        return config

    def output_string(self):

        if isinstance(self.value, int):
            rtn = f'{round(self.value, self.decimal_places):.{self.decimal_places}f}'
        else:
            list = [f'{round(val, self.decimal_places):.{self.decimal_places}f} ' for val in self.value]
            list.append(str(self.reward))
            list.append(" ")
            list.append(str(self.done))
            list.append(" ")
            list.append(str(self.info))

            rtn = ''.join(list)

        return rtn


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
