# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_architectures.ipynb (unless otherwise specified).

__all__ = ['BaseArchitecture', 'ProportionalArchitecture']

# Cell
import gym
import random
import numpy as np

import json
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
        for input in inputs:
            self.hpct.add_preprocessor(input)

    def __call__(self):
        level0config = self.config['level0']
        print(level0config)
        level0=self.configure_zerothlevel()

        """
        previous_columns=len(level0config[0])
        print('previous_columns',previous_columns)
        intermediate_levels = len(self.config)-2
        for level in range(intermediate_levels):
            if printn:
                print(f'Level{level+1}:')
                print(leveln)
            configure_level(hpct, leveln, previous_columns, level+1)
            previous_columns=levelcolumns
        """

    def get_hierarchy(self):
        return self.hpct



# Cell
class ProportionalArchitecture(BaseArchitecture):
    "Proportional Architecture"
    def __init__(self, name="proportional", config=None, env=None, input_indexes=None, **cargs):
        inputs=[]
        for ctr in range(len(input_indexes)):
            ip = IndexedParameter(index=input_indexes[ctr], name=f'Input{ctr}')
            inputs.append(ip)

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


    def configure_level(self, numInputs, level):
        inputsIndex=0
        outputsIndex=1
        referencesIndex=2

        numColumnsPreviousLevel=len(config[referencesIndex])
        numColumnsThisLevel = len(config[outputsIndex])
        #print(config[0])
        #print(numColumnsThisLevel)

        # create nodes
        for column in range(numColumnsThisLevel):
            node = PCTNode(build_links=True, mode=1)
            # change names
            node.get_function("perception").set_name(f'wsPL{level}C{column}')
            node.get_function("reference").set_name(f'wsRL{level}C{column}')
            node.get_function("comparator").set_name(f'CL{level}C{column}')
            node.get_function("output").set_name(f'pOL{level}C{column}')

            weights=[]
            # configure perceptions
            for inputIndex in range(numColumnsPreviousLevel):
                node.get_function("perception").add_link(f'wsPL{level-1}C{inputIndex}')
                weights.append(config[inputsIndex][column][inputIndex])

            node.get_function("perception").weights=np.array(weights)

            # configure outputs
            node.get_function("output").set_property('gain', config[outputsIndex][column])

            hierarchy.add_node(node, level, column)

        # configure lower references
        for referenceIndex in range(numColumnsPreviousLevel):
            reference = hierarchy.get_function(level-1, referenceIndex, "reference")
            weights=[]

            for output_column in range(numColumnsThisLevel):
                reference.add_link(f'pOL{level}C{output_column}')
                weights.append(config[referencesIndex][referenceIndex][output_column])

            reference.weights=np.array(weights)



    def configure_top_level(hierarchy, config, level):
        inputsIndex=0
        outputsIndex=1
        lowerReferencesIndex=2
        topReferencesIndex=3

        numColumnsThisLevel = len(config[topReferencesIndex])
        numColumnsPreviousLevel=len(config[lowerReferencesIndex])

        # create nodes
        for column in range(numColumnsThisLevel):
            node = PCTNode(build_links=True, mode=2, name=f'nodeL{level}C{column}')
            # change names
            #reference = Constant(config[topReferencesIndex][column], name=f'wsRL{level}C{column}')
            #node.replace_function("reference", reference, 0)
            node.get_function("perception").set_name(f'wsPL{level}C{column}')
            node.get_function("reference").set_name(f'wsRL{level}C{column}')
            node.get_function("comparator").set_name(f'CL{level}C{column}')
            node.get_function("output").set_name(f'pOL{level}C{column}')

            # set reference value
            node.get_function("reference").set_property('value', config[topReferencesIndex][column])


            weights=[]
            # configure perceptions
            for inputIndex in range(numColumnsPreviousLevel):
                node.get_function("perception").add_link(f'wsPL{level-1}C{inputIndex}')
                weights.append(config[inputsIndex][column][inputIndex])
                #weights.append(config[inputsIndex][inputIndex][column])
            node.get_function("perception").weights=np.array(weights)

            # configure outputs
            node.get_function("output").set_property('gain', config[outputsIndex][column])

            hierarchy.add_node(node, level, column)

        # configure lower references
        for referenceIndex in range(numColumnsPreviousLevel):
            reference = hierarchy.get_function(level-1, referenceIndex, "reference")
            weights=[]

            for output_column in range(numColumnsThisLevel):
                reference.add_link(f'pOL{level}C{output_column}')
                weights.append(config[lowerReferencesIndex][referenceIndex][output_column])

            reference.weights=np.array(weights)


