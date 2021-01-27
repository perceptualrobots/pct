# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_structure.ipynb (unless otherwise specified).

__all__ = ['LevelKey', 'ArchitectureStructure']

# Cell
import random
import enum
import numpy as np
from abc import ABC
from .functions import FunctionFactory
from .functions import WeightedSum
from .nodes import PCTNode

# Cell
class LevelKey(enum.Enum):
   ZERO = 'level0'
   N = 'leveln'
   TOP = 'leveltop'
   ZEROTOP = 'level0top'

# Cell
class ArchitectureStructure():
    "ArchitectureStructure"
    def __init__(self, references=None, config=None, attr_mut_pb=None, lower_float=None, upper_float=None, levels_limit=None,
                 columns_limit=None, sigma=None, mu=None, alpha=None, modes=None, **cargs):
        if config==None:
            self.config={'parameters': { 'modes' : {LevelKey.ZERO:3, LevelKey.N:3,LevelKey.TOP:4,LevelKey.ZEROTOP :4}
                        }}
            """
            self.config={'parameters': {'lower_float': -1, 'upper_float': 1,
                         'modes' : {LevelKey.ZERO:3, LevelKey.N:3,LevelKey.TOP:4,LevelKey.ZEROTOP :4},
                         'levels_limit': 3, 'columns_limit': 3, 'attr_mut_pb': 1.0,
                         'sigma': 0.8, 'mu': 0.5, 'alpha':0.6, 'attr_cx_uniform_pb':0.5},
                         LevelKey.ZERO: {'perception': {'type': 'Binary'}, 'output': {'type': 'Float'}, 'reference': {'type': 'Float'}, 'action': {'type': 'Binary'}},
                         LevelKey.N: {'perception': {'type': 'Binary'}, 'output': {'type': 'Float'}, 'reference': {'type': 'Float'}},
                         LevelKey.TOP: {'perception': {'type': 'Binary'}, 'output': {'type': 'Float'}, 'reference': {'type': 'Literal'}}}
            """
        else:
            self.config=config

        """
        if references!=None:
            self.add_config_parameter(LevelKey.TOP , 'reference', 'value', references )


        if attr_mut_pb != None:
            self.config['parameters']['attr_mut_pb']=attr_mut_pb
        if lower_float!=None:
            self.config['parameters']['lower_float']=lower_float
        if upper_float!=None:
            self.config['parameters']['upper_float']=upper_float
        if levels_limit!=None:
            self.config['parameters']['levels_limit']=levels_limit
        if columns_limit!=None:
            self.config['parameters']['columns_limit']=columns_limit
        if sigma!=None:
            self.config['parameters']['sigma']=sigma
        if mu!=None:
            self.config['parameters']['mu']=mu
        if alpha!=None:
            self.config['parameters']['alpha']=alpha
        """
        if modes!=None:
            self.config['parameters']['modes']=modes


    def get_config(self):
        return self.config

    """
    def add_config_type(self, level_key=None, function=None, type=None):
        ttype={'type': type}
        self.config[level_key][function]=ttype

    def add_structure_parameter(self, key=None, value=None):
        self.config['parameters'][key]=value

    def add_level_parameter(self, level=None, function=None, key=None, value=None):
        self.config[level][function][key]=value


    def add_config_parameter(self, level_key=LevelKey.N, function=None,  parameter_type=None, parameter_value=None):
        if not 'pars' in self.config[level_key][function]:
            self.config[level_key][function]['pars']={} #pars={'pars'}
        self.config[level_key][function]['pars'][parameter_type]=parameter_value

    def get_config_parameter(self, level_key=LevelKey.N, function=None,  parameter_type=None):
        if not 'pars' in self.config[level_key][function]:
            return False
        return self.config[level_key][function]['pars'][parameter_type]

    def get_level0_config(self):
        return self.config['level0']

    def get_leveln_config(self):
        return self.config['leveln']

    def get_leveltop_config(self):
        return self.config['leveltop']

    def get_type(self, level_key, function):
        package = self.config[level_key][function]
        pars={}
        if 'pars' in package.keys():
            pars = package['pars']

        return package['type'], pars
    """

    """
    def get_function_type(self, mode, function):
        type = 'WeightedSum'

        if mode == 4:
            if function == 'reference':
                type = 'Constant'

            if function == 'output':
                type = 'WeightedSum'

        if mode == 5:
            if function == 'reference':
                type = 'Constant'

            if function == 'output':
                type = 'SmoothWeightedSum'



        return type
    """



    def set_node_function(self, node, function, mode, thislevel, targetlevel, targetprefix, column, num_target_indices, inputs, input_weights, by_column):
        type = PCTNode.get_function_type(mode, function)
        function_type = FunctionFactory.createFunction(type)
        function_type.set_node_function(node, function,  thislevel, targetlevel, targetprefix, column, num_target_indices, inputs, input_weights, by_column)


    def get_parameter(self, key):
        return self.config['parameters'][key]


    """

    def get_type_parameters(self, level, function):
        return self.config[level][function]


    def get_list(self, level_key, function,  num_lists, num_items):
        parameter = self.get_parameter_object(level_key, function)
        return parameter.get_weights_list(num_lists, num_items)

    def mutate_list(self, level, function, wts):
        parameter = self.get_parameter_object(level, function)
        return parameter.mutate(wts)

    def mutate_binary_lists(self, level, function, lists):
        parameter = self.get_parameter_object(level, function)
        parameter.mutate_binary_lists(lists)

    def mate_lists(self, level, function, wts1, wts2):
        parameter = self.get_parameter_object(level, function)
        return parameter.mate(wts1, wts2)

    def ensure_non_zero(self, level, function, wts):
        parameter = self.get_parameter_object(level, function)
        return parameter.ensure_non_zero(wts)

    def copy_data(self, level, function, from_wts, to_wts):
        parameter = self.get_parameter_object(level, function)
        parameter.copy_data(from_wts, to_wts)
    """

    """

    def get_parameter_object(self, level_key, function):
        type, type_parameters = self.get_type(level_key, function)

        parameter = ParameterFactory.createParameter(type)
        parameter.set_parameters(type_parameters, self.config['parameters'])

        return parameter


    def get_level0(self, num_inputs, numColumnsThisLevel, numColumnsNextLevel, num_actions):
        config0=[]

        perception_list = self.get_list(LevelKey.ZERO,'perception', num_inputs, numColumnsThisLevel)
        output_list = self.get_list(LevelKey.ZERO,'output', num_actions, numColumnsThisLevel)
        reference_list = self.get_list(LevelKey.ZERO,'reference', numColumnsThisLevel, numColumnsNextLevel)
        action_list = self.get_list(LevelKey.ZERO,'action', num_actions, numColumnsThisLevel)

        config0.append(perception_list)
        config0.append(output_list[0])
        config0.append(reference_list)
        config0.append(action_list)

        return config0


    def get_leveln(self, numColumnsThisLevel, numColumnsNextLevel, numColumnsPreviousLevel):
        config=[]

        perception_list = self.get_list(LevelKey.N,'perception', numColumnsPreviousLevel, numColumnsThisLevel)

        output_list = self.get_list(LevelKey.N,'output', numColumnsPreviousLevel, numColumnsThisLevel)

        reference_list = self.get_list(LevelKey.N,'reference', numColumnsThisLevel, numColumnsNextLevel)


        config.append(perception_list)
        config.append(output_list[0])
        config.append(reference_list)

        return config

    def get_level0top(self, num_inputs, numColumnsThisLevel, num_actions):
        config0=[]

        perception_list = self.get_list(LevelKey.ZERO,'perception', num_inputs, numColumnsThisLevel)

        output_list = self.get_list(LevelKey.ZERO,'output', num_actions, numColumnsThisLevel)

        reference_list = self.get_list(LevelKey.TOP,'reference', 1, numColumnsThisLevel)

        action_list = self.get_list(LevelKey.ZERO,'action', num_actions, numColumnsThisLevel)

        config0.append(perception_list)
        config0.append(output_list[0])
        config0.append(reference_list)
        config0.append(action_list)

        return config0

    def get_leveltop(self, numColumnsThisLevel, numColumnsPreviousLevel):
        config=[]

        perception_list = self.get_list(LevelKey.TOP,'perception', numColumnsPreviousLevel, numColumnsThisLevel)

        output_list = self.get_list(LevelKey.TOP,'output', 1, numColumnsThisLevel)

        reference_list = self.get_list(LevelKey.TOP,'reference', 1, numColumnsThisLevel)


        config.append(perception_list)
        config.append(output_list[0])
        config.append(reference_list)

        return config
    """

    def set_output_function(self, node, mode, thislevel, column, input_weights):
        type = PCTNode.get_function_type(mode, function)
        function_type = FunctionFactory.createFunction(type)
        function_type.set_output_function(node, function,  thislevel, column, input_weights)


    # assume same for all levels and that datatypes are always floats
    """
    def set_output_function(self, node,  thislevel, column, input_weights):
        func = node.get_function('output')
        func.set_name(f'OL{thislevel}C{column}ws')

        weights=[]
        weights.append(input_weights[column])
        func.weights=np.array(weights)
    """

    def set_action_function(self, hpct, env, numColumnsThisLevel,  weights):
        numActions = len(weights)
        for actionIndex in range(numActions):
            action = WeightedSum(weights=weights[actionIndex], name=f'Action{actionIndex+1}ws')
            for column in range(numColumnsThisLevel):
                action.add_link(f'OL0C{column}ws')
            hpct.add_postprocessor(action)
            env.add_link(action)