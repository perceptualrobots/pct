# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/14_helpers.ipynb.

# %% auto 0
__all__ = ['ListChecker', 'ARCDataProcessor']

# %% ../nbs/14_helpers.ipynb 3
import math
import numpy as np

# %% ../nbs/14_helpers.ipynb 4
import math

class ListChecker:
    @staticmethod
    def check_list_unchanged(float_list, rel_tol=1e-6, abs_tol=0.0):
        if not float_list:  # Check if the list is empty
            return True
        first_value = float_list[0]
        for value in float_list[1:]:
            if not math.isclose(value, first_value, rel_tol=rel_tol, abs_tol=abs_tol):
                return False
        return True

    @staticmethod
    def check_integer_list_unchanged(int_list):
        if not int_list:  # Check if the list is empty
            return True
        first_value = int_list[0]
        for value in int_list[1:]:
            if value != first_value:
                return False
        return True


# %% ../nbs/14_helpers.ipynb 6
class ARCDataProcessor:
    def __init__(self, config_dict, arc_dict):
        self.grid_shape = config_dict.get('grid_shape')
        if self.grid_shape not in {'equal', 'unequal', None}:
            raise ValueError("grid_shape must be 'equal', 'unequal', or None")
        
        self.input_set = config_dict.get('input_set', 'both')
        if self.input_set not in {'env_only', 'inputs_only', 'both'}:
            raise ValueError("input_set must be 'env_only', 'inputs_only', 'both'")
        
        self.action_set = config_dict.get('action_set', None)
        if self.action_set not in {'dims_only', None}:
            raise ValueError("action_set must be 'dims_only' or None")
        
        self.index = config_dict.get('index', 0)
        self.initial_index = self.index if 'index' in config_dict else None

        self.arc_dict = arc_dict
        self.create_env()

    def add_rows(self, num_rows):
        num_rows = round(num_rows)
        self.env = np.pad(self.env, ((0, num_rows), (0, 0)), mode='constant', constant_values=0)

    def remove_rows(self, num_rows):
        num_rows = round(num_rows)
        if num_rows >= self.env.shape[0]:
            num_rows = self.env.shape[0] - 1
        self.env = self.env[:-num_rows, :] if self.env.shape[0] > num_rows else self.env

    def add_columns(self, num_columns):
        num_columns = round(num_columns)
        self.env = np.pad(self.env, ((0, 0), (0, num_columns)), mode='constant', constant_values=0)

    def remove_columns(self, num_columns):
        num_columns = round(num_columns)
        if num_columns >= self.env.shape[1]:
            num_columns = self.env.shape[1] - 1
        self.env = self.env[:, :-num_columns] if self.env.shape[1] > num_columns else self.env

    def process_remaining_values(self, values):
        for i, value in enumerate(values):
            row, col = divmod(i, self.env.shape[1])
            if row < self.env.shape[0] and col < self.env.shape[1]:
                self.env[row, col] = value

    def get_array(self, key, index, sub_key):
        return np.array(self.arc_dict[key][index][sub_key]).flatten()

    def next(self):
        if self.initial_index is not None:
            return False
        self.index += 1
        self.create_env()
        return True

    def reset(self):
        if self.initial_index is None:
            self.index = 0
        else:
            self.index = self.initial_index
        self.create_env()

    def create_env(self):
        self.env = np.array(self.arc_dict['train'][self.index]['input'])

    def process_dimensions(self, actions):
        if len(actions) == 2:
            num_rows, num_cols = actions
        elif len(actions) == 1:
            num_rows = num_cols = actions[0]
        else:
            raise ValueError("Actions must have one or two values")

        if num_rows > 0:
            self.add_rows(num_rows)
        elif num_rows < 0:
            self.remove_rows(abs(num_rows))

        if num_cols > 0:
            self.add_columns(num_cols)
        elif num_cols < 0:
            self.remove_columns(abs(num_cols))

    def get_input_dimensions(self):
        return np.array(self.arc_dict['train'][self.index]['input']).shape

    def get_output_dimensions(self):
        return np.array(self.arc_dict['train'][self.index]['output']).shape

    def get_env_dimensions(self):
        return self.env.shape

    def apply_actions(self, actions):
        value_index = 0
        if self.grid_shape == 'equal':
            self.process_dimensions(actions[:1])
            value_index = 1
        elif self.grid_shape == 'unequal':
            self.process_dimensions(actions[:2])
            value_index = 2
        
        if self.action_set != 'dims_only':
            self.process_remaining_values(actions[value_index:])

    def get_state(self):
        values = []
        info = {}
        info['dims'] = 0

        if self.grid_shape == 'equal':
            if self.input_set in {'env_only', 'both'}:
                values.append(self.get_env_dimensions()[1])
                info['dims'] += 1
            if self.input_set in {'inputs_only', 'both'}:
                values.append(self.get_input_dimensions()[1])
                info['dims'] += 1
            values.append(self.get_output_dimensions()[1])
            info['dims'] += 1
        elif self.grid_shape == 'unequal':
            if self.input_set in {'env_only', 'both'}:
                values.extend(self.get_env_dimensions())
                info['dims'] += 2
            if self.input_set in {'inputs_only', 'both'}:
                values.extend(self.get_input_dimensions())
                info['dims'] += 2
            values.extend(self.get_output_dimensions())
            info['dims'] += 2

        if self.action_set != 'dims_only':
            if self.input_set in {'env_only', 'both'}:
                flattened_env = self.env.flatten()
                values.extend(flattened_env)
                info['env'] = len(flattened_env)
            
            if self.input_set in {'inputs_only', 'both'}:
                flattened_input = self.get_array('train', self.index, 'input')
                values.extend(flattened_input)
                info['inputs'] = len(flattened_input)

            flattened_output = self.get_array('train', self.index, 'output')
            values.extend(flattened_output)
            info['outputs'] = len(flattened_output)

        return values, info

    def fitness_function(self):
        output_array = np.array(self.arc_dict['train'][self.index]['output'])
        env_array = self.env

        # First metric: square of the difference between the dimensions
        dim_metric = (env_array.shape[0] - output_array.shape[0]) ** 2 + (env_array.shape[1] - output_array.shape[1]) ** 2

        # Second metric: square of the difference between each element in the arrays
        element_metric = 0
        for i in range(max(env_array.shape[0], output_array.shape[0])):
            for j in range(max(env_array.shape[1], output_array.shape[1])):
                env_value = env_array[i, j] if i < env_array.shape[0] and j < env_array.shape[1] else None
                output_value = output_array[i, j] if i < output_array.shape[0] and j < output_array.shape[1] else None
                if env_value is None or output_value is None:
                    element_metric += 25
                else:
                    element_metric += (env_value - output_value) ** 2

        # Final metric
        if self.action_set == 'dims_only':
            final_metric = dim_metric
        else:
            final_metric = dim_metric + element_metric

        return final_metric

    def get_train_input(self):
        return np.array(self.arc_dict['train'][self.index]['input'])

    def get_train_output(self):
        return np.array(self.arc_dict['train'][self.index]['output'])

    def get_test_input(self):
        return np.array(self.arc_dict['test'][0]['input'])  # Assuming only one test case as per the provided format


