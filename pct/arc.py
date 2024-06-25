# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/15_arc.ipynb.

# %% auto 0
__all__ = ['ARCEnv']

# %% ../nbs/15_arc.ipynb 3
import json, os
import numpy as np
import gym
from gym import spaces
# import copy

# %% ../nbs/15_arc.ipynb 4
class ARCEnv(gym.Env):
    def __init__(self):
        super(ARCEnv, self).__init__()
        self.index = 0
        self.env = None
        self.dimensions = []
        self.fitness = 0.0
        self.state = []
        self.done = False

    def initialise(self, file_name, properties):
        with open(file_name, 'r') as f:
            data = json.load(f)
        
        self.index = properties.get('index', 0)
        self.train_data = data['train']
        self.test_data = data['test']
        self.inputs = [x['input'] for x in self.train_data]
        self.outputs = [x.get('output', []) for x in self.train_data]
        self.reset()

    def get_train_array(self, idx):
        return self.train_data[idx]

    def get_input_array(self, idx):
        return self.inputs[idx]

    def get_output_array(self, idx):
        return self.outputs[idx]

    def get_element(self, array, row, col):
        return array[row][col]

    def get_dimensions(self):
        return self.dimensions

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index
        self.reset()

    def add_rows(self, num_rows):
        self.env = np.pad(self.env, ((0, num_rows), (0, 0)), mode='constant', constant_values=0)

    def remove_rows(self, num_rows):
        self.env = self.env[:-num_rows, :]

    def add_columns(self, num_columns):
        self.env = np.pad(self.env, ((0, 0), (0, num_columns)), mode='constant', constant_values=0)

    def remove_columns(self, num_columns):
        self.env = self.env[:, :-num_columns]

    def fitness_function(self):
        output = np.array(self.outputs[self.index])
        self.set_dimensions()

        # First metric: Squared difference in dimensions
        # dim_metric = (self.env.shape[0] - output.shape[0]) ** 2 + (self.env.shape[1] - output.shape[1]) ** 2
        dim_metric = (self.dimensions[0] - self.dimensions[2]) ** 2 + (self.dimensions[1] - self.dimensions[3]) ** 2

        # Second metric: Squared difference in elements
        element_metric = 0
        for i in range(max(self.env.shape[0], output.shape[0])):
            for j in range(max(self.env.shape[1], output.shape[1])):
                env_val = self.env[i, j] if i < self.env.shape[0] and j < self.env.shape[1] else None
                output_val = output[i, j] if i < output.shape[0] and j < output.shape[1] else None
                if env_val is None or output_val is None:
                    element_metric += 25
                else:
                    element_metric += (env_val - output_val) ** 2

        # temp
        element_metric = 0

        # Final metric: Sum of the two metrics
        final_metric = dim_metric + element_metric
        return final_metric

    def step(self, action):
        num_rows, num_cols, *values = action

        if num_rows > 0:
            self.add_rows(num_rows)
        elif num_rows < 0:
            self.remove_rows(abs(num_rows))
        
        if num_cols > 0:
            self.add_columns(num_cols)
        elif num_cols < 0:
            self.remove_columns(abs(num_cols))
        
        for i, value in enumerate(values):
            row, col = divmod(i, self.env.shape[1])
            if row < self.env.shape[0] and col < self.env.shape[1]:
                self.env[row, col] = value

        self.fitness = self.fitness_function()
        if self.fitness < 1e-6:
            self.done = True
        
        self.state = self.env.flatten().tolist()
        return self.state, self.fitness, self.done

    def set_dimensions(self):
        self.dimensions = [len(self.env[0]), len(self.env), len(self.outputs[self.index][0]), len(self.outputs[self.index])]


    def reset(self):
        self.env = np.array(self.inputs[self.index])
        self.set_dimensions()
        self.fitness = self.fitness_function()
        self.done = False
        self.state = self.env.flatten().tolist()
        return self.state


