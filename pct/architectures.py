# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_architectures.ipynb (unless otherwise specified).

__all__ = ['BaseArchitecture', 'ProportionalArchitecture']

# Cell
import gym
import random
import numpy as np
import os
from abc import ABC, abstractmethod
from .hierarchy import PCTHierarchy
from .nodes import PCTNode
from .functions import WeightedSum

# Cell
class BaseArchitecture(ABC):
    "Base class of an array architecture. This class is not used direclty by developers, but defines the functionality common to all."
    def __init__(self, name, config, env, inputs):
        self.config = config
        self.env = env
        self.inputs=inputs
        self.hpct = PCTHierarchy()

    def __call__(self):
        level0config = self.config['level0']
        print(level0config)
        level0=self.configure_zerothlevel()




# Cell
class ProportionalArchitecture(BaseArchitecture):
    "Proportional Architecture"
    def __init__(self, name="proportional", config=None, env=None, inputs=None, **cargs):
        super().__init__(name, config, env, inputs)



    def configure_zerothlevel(self):
        inputsIndex=0
        outputsIndex=1
        actionsIndex=2

        config=self.config['level0']
        level=0
        numInputs= len(self.inputs)
        columns = len(config[inputsIndex][0])
        #print(config[0][0])
        #print(columns)

        # create nodes
        for column in range(columns):
            node = PCTNode(build_links=True, mode=1)
            # change names
            node.get_function("perception").set_name(f'wsPL{level}C{column}')
            node.get_function("reference").set_name(f'wsRL{level}C{column}')
            node.get_function("comparator").set_name(f'CL{level}C{column}')
            node.get_function("output").set_name(f'pOL{level}C{column}')

            weights=[]
            # configure perceptions
            for inputIndex in range(numInputs):
                node.get_function("perception").add_link(self.inputs[inputIndex])
                weights.append(config[inputsIndex][inputIndex][column])
            node.get_function("perception").weights=np.array(weights)

            # configure outputs
            node.get_function("output").set_property('gain', config[outputsIndex][column])

            self.hpct.add_node(node, level, column)

        # configure actions
        numActions = len(config[actionsIndex])
        numColumnsThisLevel = len(config[outputsIndex])
        for actionIndex in range(numActions):
            action = WeightedSum(weights=config[actionsIndex][actionIndex], name=f'action{actionIndex+1}')
            for column in range(numColumnsThisLevel):
                action.add_link(f'pOL{level}C{column}')
            self.hpct.add_postprocessor(action)
            self.env.add_link(action)


