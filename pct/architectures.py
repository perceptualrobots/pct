# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_architectures.ipynb (unless otherwise specified).

__all__ = ['BaseArchitecture', 'ProportionalArchitecture', 'LevelKey', 'ControlUnitIndices', 'DynamicArchitecture']

# Cell
import random
import numpy as np
import json
import os
import enum
from abc import ABC, abstractmethod
from .hierarchy import PCTHierarchy
from .nodes import PCTNode
from .functions import WeightedSum
from .functions import IndexedParameter
from .functions import Constant
from .environments import PendulumV0

# Cell
class BaseArchitecture(ABC):
    "Base class of an array architecture. This class is not used direclty by developers, but defines the functionality common to all."
    def __init__(self, name, config, env, inputs, history, error_collector):
        self.config = config
        self.env = env
        self.inputs=inputs
        self.hpct = PCTHierarchy(history=history, error_collector=error_collector)
        self.hpct.add_preprocessor(env)

        for input in inputs:
            self.hpct.add_preprocessor(input)

    def __call__(self):
        #level0config = self.config['level0']
        previous_columns=self.configure_zerothlevel()

        intermediate_levels = len(self.config)-3
        level=-1
        for level in range(intermediate_levels):
            leveln = self.config[f'level{level+1}']
            levelcolumns = self.configure_level(leveln, previous_columns, level+1)
            previous_columns=levelcolumns
        if intermediate_levels < 0:
            self.set_references()
        else:
            level+=1
            self.configure_top_level(self.config[f'level{level+1}'], level+1)

    def get_hierarchy(self):
        return self.hpct




# Cell
class ProportionalArchitecture(BaseArchitecture):
    "Proportional Architecture"
    def __init__(self, name="proportional", config=None, env=None, input_indexes=None, history=False, error_collector=None, **cargs):
        inputs=[]
        for ctr in range(len(input_indexes)):
            ip = IndexedParameter(index=input_indexes[ctr], name=f'Input{ctr}', links=[env])
            inputs.append(ip)

        super().__init__(name, config, env, inputs, history, error_collector)

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
            node = PCTNode(build_links=True, mode=1, name=f'L{level}C{column}', history=self.hpct.history)
            # change names
            node.get_function("perception").set_name(f'PL{level}C{column}ws')
            node.get_function("reference").set_name(f'RL{level}C{column}ws')
            node.get_function("comparator").set_name(f'CL{level}C{column}')
            node.get_function("output").set_name(f'OL{level}C{column}p')

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
            action = WeightedSum(weights=config[actionsIndex][actionIndex], name=f'Action{actionIndex+1}ws')
            for column in range(numColumnsThisLevel):
                action.add_link(f'OL{level}C{column}p')
            self.hpct.add_postprocessor(action)
            self.env.add_link(action)

        return numColumnsThisLevel

    def configure_level(self, config, numColumnsPreviousLevel, level):
        inputsIndex=0
        outputsIndex=1
        referencesIndex=2

        #numColumnsPreviousLevel=len(config[referencesIndex])
        numColumnsThisLevel = len(config[outputsIndex])

        # create nodes
        for column in range(numColumnsThisLevel):
            node = PCTNode(build_links=True, mode=1, name=f'L{level}C{column}', history=self.hpct.history)
            # change names
            node.get_function("perception").set_name(f'PL{level}C{column}ws')
            node.get_function("reference").set_name(f'RL{level}C{column}ws')
            node.get_function("comparator").set_name(f'CL{level}C{column}')
            node.get_function("output").set_name(f'OL{level}C{column}p')

            weights=[]
            # configure perceptions
            for inputIndex in range(numColumnsPreviousLevel):
                node.get_function("perception").add_link(f'PL{level-1}C{inputIndex}ws')
                weights.append(config[inputsIndex][column][inputIndex])

            node.get_function("perception").weights=np.array(weights)

            # configure outputs
            node.get_function("output").set_property('gain', config[outputsIndex][column])

            self.hpct.add_node(node, level, column)

        # configure lower references
        for referenceIndex in range(numColumnsPreviousLevel):
            reference = self.hpct.get_function(level-1, referenceIndex, "reference")
            weights=[]

            for output_column in range(numColumnsThisLevel):
                reference.add_link(f'OL{level}C{output_column}p')
                weights.append(config[referencesIndex][referenceIndex][output_column])

            reference.weights=np.array(weights)

        return numColumnsThisLevel

    def configure_top_level(self, config, level):
        inputsIndex=0
        outputsIndex=1
        lowerReferencesIndex=2
        topReferencesIndex=3

        numColumnsThisLevel = len(config[topReferencesIndex])
        numColumnsPreviousLevel=len(config[lowerReferencesIndex])

        # create nodes
        for column in range(numColumnsThisLevel):
            node = PCTNode(build_links=True, mode=2, name=f'L{level}C{column}', history=self.hpct.history)
            # change names
            reference = Constant(config[topReferencesIndex][column], name=f'RL{level}C{column}c')
            node.replace_function("reference", reference, 0)
            node.get_function("perception").set_name(f'PL{level}C{column}ws')
            #node.get_function("reference").set_name(f'RL{level}C{column}ws')
            node.get_function("comparator").set_name(f'CL{level}C{column}')
            node.get_function("output").set_name(f'OL{level}C{column}p')
            node.get_function("comparator").set_link(reference)
            node.get_function("comparator").add_link(node.get_function("perception"))

            # set reference value
            #node.get_function("reference").set_property('value', config[topReferencesIndex][column])


            weights=[]
            # configure perceptions
            for inputIndex in range(numColumnsPreviousLevel):
                node.get_function("perception").add_link(f'PL{level-1}C{inputIndex}ws')
                weights.append(config[inputsIndex][column][inputIndex])
                #weights.append(config[inputsIndex][inputIndex][column])
            node.get_function("perception").weights=np.array(weights)

            # configure outputs
            node.get_function("output").set_property('gain', config[outputsIndex][column])

            self.hpct.add_node(node, level, column)

        # configure lower references
        for referenceIndex in range(numColumnsPreviousLevel):
            reference = self.hpct.get_function(level-1, referenceIndex, "reference")
            weights=[]

            for output_column in range(numColumnsThisLevel):
                reference.add_link(f'OL{level}C{output_column}p')
                weights.append(config[lowerReferencesIndex][referenceIndex][output_column])

            reference.weights=np.array(weights)


    def set_references(self):
        level=0
        config=self.config['level0']
        topReferencesIndex=3

        numColumnsThisLevel = len(config[topReferencesIndex])
        # change nodes
        for column in range(numColumnsThisLevel):
            node = self.hpct.get_node(level, column)
            reference = Constant(config[topReferencesIndex][column], name=f'RL{level}C{column}c')
            node.replace_function("reference", reference, 0)
            node.get_function("comparator").set_link(reference)
            node.get_function("comparator").add_link(node.get_function("perception"))





# Cell
class LevelKey(enum.Enum):
   ZERO = 'level0'
   N = 'leveln'
   TOP = 'leveltop'
   ZEROTOP = 'level0top'

# Cell
class ControlUnitIndices(enum.IntEnum):
   PER_INDEX = 0
   OUT_INDEX = 1
   REF_INDEX = 2
   ACT_INDEX = 3

# Cell



class DynamicArchitecture(BaseArchitecture):
    "Dynamic Architecture"
    def __init__(self, name="dynamic", structure=None, config=None, env=None, input_indexes=None, history=False, error_collector=None, **cargs):
        inputs=[]
        for ctr in range(len(input_indexes)):
            ip = IndexedParameter(index=input_indexes[ctr], name=f'Input{ctr}', links=[env])
            inputs.append(ip)

        super().__init__(name, config, env, inputs, history, error_collector)
        self.structure=structure

    def __call__(self):
        #level0config = self.config['level0']
        levels = len(self.config)-1
        #print('levels', levels)
        if levels == 1:
            self.configure_zerotoplevel()
        else:
            previous_columns=self.configure_zerothlevel()

            intermediate_levels = len(self.config)-3
            level=-1
            for level in range(intermediate_levels):
                leveln = self.config[f'level{level+1}']
                levelcolumns = self.configure_level(leveln, previous_columns, level+1)
                previous_columns=levelcolumns
            if intermediate_levels < 0:
                self.set_references()
            else:
                level+=1
                self.configure_top_level(self.config[f'level{level+1}'], level+1, previous_columns)


    def configure_zerotoplevel(self):
        mode = self.structure.get_parameter('modes')[LevelKey.ZEROTOP]

        inputsIndex=0
        outputsIndex=1
        referencesIndex=2
        actionsIndex=3

        config=self.config['level0']
        level=0
        #numInputs= len(self.inputs)
        columns = len(config[inputsIndex][0])
        #print(config[0][0])
        #print('columns',columns)

        # create nodes
        for column in range(columns):
            node = PCTNode(build_links=True, mode=mode, name=f'L{level}C{column}', history=self.hpct.history)
            self.structure.set_node_function(node, 'reference', LevelKey.TOP , level, None, None, column, None, None, config[referencesIndex], True)
            self.structure.set_node_function(node, 'perception', LevelKey.ZERO, level, None, None, column, len(self.inputs), self.inputs, config[inputsIndex], False)

            comparator_name=f'CL{level}C{column}'
            node.get_function("comparator").set_name(comparator_name)
            node.get_function("comparator").set_link(node.get_function("reference"))
            node.get_function("comparator").add_link(node.get_function("perception"))

            self.structure.set_output_function(node, level, column, config[outputsIndex])

            self.hpct.add_node(node, level, column)

        # configure actions
        numColumnsThisLevel = len(config[outputsIndex])
        self.structure.set_action_function(self.hpct, self.env, numColumnsThisLevel, config[actionsIndex])

        return numColumnsThisLevel

    def configure_zerothlevel(self):
        mode = self.structure.get_parameter('modes')[LevelKey.ZERO]

        inputsIndex=0
        outputsIndex=1
        referencesIndex=2
        actionsIndex=3

        config=self.config['level0']
        level=0
        columns = len(config[inputsIndex][0])
        #print(config[0][0])
        #print(columns)
        columnsNextLevel = len(config[referencesIndex][0])
        #print('columnsNextLevel',columnsNextLevel)

        # create nodes
        for column in range(columns):
            node = PCTNode(build_links=True, mode=mode, name=f'L{level}C{column}', history=self.hpct.history)
            self.structure.set_node_function(node, 'reference', LevelKey.ZERO, level, level+1, 'O', column, columnsNextLevel, None, config[referencesIndex], True)
            self.structure.set_node_function(node, 'perception', LevelKey.ZERO, level, None, None, column, len(self.inputs), self.inputs, config[inputsIndex], False)

            comparator_name=f'CL{level}C{column}'
            node.get_function("comparator").set_name(comparator_name)

            self.structure.set_output_function(node, level, column, config[outputsIndex])

            self.hpct.add_node(node, level, column)

        # configure actions
        numColumnsThisLevel = len(config[outputsIndex])
        self.structure.set_action_function(self.hpct, self.env, numColumnsThisLevel, config[actionsIndex])

        return numColumnsThisLevel

    def configure_level(self, config, numColumnsPreviousLevel, level):
        mode = self.structure.get_parameter('modes')[LevelKey.N]

        inputsIndex=0
        outputsIndex=1
        referencesIndex=2

        #numColumnsPreviousLevel=len(config[referencesIndex])
        numColumnsThisLevel = len(config[outputsIndex])
        columnsNextLevel = len(config[referencesIndex][0])

        # create nodes
        for column in range(numColumnsThisLevel):
            node = PCTNode(build_links=True, mode=mode, name=f'L{level}C{column}', history=self.hpct.history)
            self.structure.set_node_function(node, 'reference', LevelKey.N, level, level+1, 'O', column, columnsNextLevel, None, config[referencesIndex], True)
            self.structure.set_node_function(node, 'perception', LevelKey.N, level, level-1, 'P', column, numColumnsPreviousLevel, None, config[inputsIndex], False)

            comparator_name=f'CL{level}C{column}'
            node.get_function("comparator").set_name(comparator_name)

            self.structure.set_output_function(node, level, column, config[outputsIndex])

            self.hpct.add_node(node, level, column)

        return numColumnsThisLevel

    def configure_top_level(self, config, level, numColumnsPreviousLevel ):
        mode = self.structure.get_parameter('modes')[LevelKey.TOP]
        inputsIndex=0
        outputsIndex=1
        referencesIndex=2

        numColumnsThisLevel = len(config[referencesIndex])

        # create nodes
        for column in range(numColumnsThisLevel):
            node = PCTNode(build_links=True, mode=mode, name=f'L{level}C{column}', history=self.hpct.history)

            self.structure.set_node_function(node, 'reference', LevelKey.TOP , level, None, None, column, None, None, config[referencesIndex], None)
            self.structure.set_node_function(node, 'perception', LevelKey.TOP , level, level-1, 'P', column, numColumnsPreviousLevel, None, config[inputsIndex], False)

            comparator_name=f'CL{level}C{column}'
            node.get_function("comparator").set_name(comparator_name)
            node.get_function("comparator").set_link(node.get_function('reference'))
            node.get_function("comparator").add_link(node.get_function('perception'))

            self.structure.set_output_function(node, level, column, config[outputsIndex])

            self.hpct.add_node(node, level, column)


