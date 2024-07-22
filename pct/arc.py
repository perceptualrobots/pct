# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/15_arc.ipynb.

# %% auto 0
__all__ = ['ARCDataProcessor', 'ARCEnv']

# %% ../nbs/15_arc.ipynb 3
import json, os
import numpy as np
import gym
from gym import spaces
from time import sleep
import pygame
from matplotlib import colors       
# import copy

# %% ../nbs/15_arc.ipynb 4
from .putils import limit_large_float

# %% ../nbs/15_arc.ipynb 5
class ARCDataProcessor:
    def __init__(self, config_dict, arc_dict):
        self.arc_dict = arc_dict
        self.grid_shape = self.determine_grid_shape()
        
        if 'grid_shape' in config_dict:
            self.grid_shape = config_dict.get('grid_shape')
        
        self.input_set = config_dict.get('input_set', ['default'])
        if not all(item in {'env', 'inputs', 'outputs'} for item in self.input_set):
            raise ValueError("input_set must be a list containing 'env', 'inputs', and/or 'outputs'")
        
        if 'env' not in self.input_set:
            raise ValueError("input_set must contain 'env' at least.")
        
        self.control_set = config_dict.get('control_set', ['default'])
        if not all(item in {'dims', 'cells'} for item in self.control_set):
            raise ValueError("control_set must be a list containing 'dims' and/or 'cells'")
        
        self.index = config_dict.get('index', 0)
        self.initial_index = self.index if 'index' in config_dict else None
        self.dataset = config_dict.get('dataset', None)

        if self.dataset is None:
            raise ValueError("dataset must be provided in config_dict")

        if 'dims' in self.control_set and self.grid_shape is None:
            raise ValueError("grid_shape cannot be None when 'dims' is in control_set")

        self.create_env()
        self.info = self.create_info()

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
        if len(values) != self.env.shape[0] * self.env.shape[1]:
            raise Exception("Mismatch in number of elements in actions and env.")
        for i, value in enumerate(values):
            row, col = divmod(i, self.env.shape[1])
            if row < self.env.shape[0] and col < self.env.shape[1]:
                self.env[row, col] += value

    def get_array(self, key, index, sub_key):
        return np.array(self.arc_dict[key][index][sub_key])

    def next(self):
        if self.index >= len(self.arc_dict[self.dataset]):
            return False
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
        self.env = np.array(self.arc_dict[self.dataset][self.index]['input'])

    def process_dimensions(self, actions):
        if len(actions) == 2:
            num_rows, num_cols = actions
        elif len(actions) == 1:
            num_rows = num_cols = actions[0]
        else:
            raise ValueError("Actions must have one or two values")

        num_rows = limit_large_float(num_rows, 10000)
        num_cols = limit_large_float(num_cols, 10000)

        if num_rows > 0:
            self.add_rows(num_rows)
        elif num_rows < 0:
            self.remove_rows(abs(num_rows))

        if num_cols > 0:
            self.add_columns(num_cols)
        elif num_cols < 0:
            self.remove_columns(abs(num_cols))

    def get_input_dimensions(self):
        return np.array(self.arc_dict[self.dataset][self.index]['input']).shape

    def get_output_dimensions(self):
        return np.array(self.arc_dict[self.dataset][self.index]['output']).shape

    def get_env_dimensions(self):
        return self.env.shape

    def apply_actions(self, actions):
        if len(actions) != self.info['num_actions']:
            raise Exception(f'Number of actions from hierarchy {len(actions)} should equal expected actions {self.info["num_actions"]}.')
        value_index = 0
        if 'dims' in self.control_set:
            if self.grid_shape == 'equal':
                self.process_dimensions(actions[:1])
                value_index = 1
            elif self.grid_shape == 'unequal':
                self.process_dimensions(actions[:2])
                value_index = 2
        
        if 'cells' in self.control_set:
            self.process_remaining_values(actions[value_index:])

    def create_info(self):
        info = {}
        info['num_actions'] = 0

        if 'dims' in self.control_set:
            info['grid_shape'] = self.grid_shape

            if self.grid_shape == 'equal':
                info['num_actions'] = 1
                info['dims'] = len(self.input_set)
            elif self.grid_shape == 'unequal':
                info['num_actions'] = 2
                info['dims'] = len(self.input_set)*2

        if 'cells' in self.control_set:
            if 'env' in self.input_set:
                edims = self.get_env_dimensions()
                info['env'] = edims
                info['num_actions'] += edims[0]*edims[1]
            
            if 'inputs' in self.input_set:
                idims = self.get_input_dimensions()
                info['inputs'] = idims
                # info['num_actions'] += idims[0]*idims[1]

            if 'outputs' in self.input_set:
                odims =  self.get_output_dimensions()
                info['outputs'] = odims
                # info['num_actions'] +=  odims[0]*odims[1]

        return info

    def get_state(self):
        state = {'inputs':{}}
        self.info['num_actions'] = 0

        def set_state_dimensions(dic, state_key, dimensions):
            if state_key in self.input_set:
                dic[state_key] = dimensions
                # self.info['num_actions'] += 1

        if 'dims' in self.control_set:
            dims = {}
            if self.grid_shape == 'equal':
                self.info['num_actions'] = 1
                set_state_dimensions(dims, 'env', (self.get_env_dimensions()[1],))
                set_state_dimensions(dims, 'inputs', (self.get_input_dimensions()[1],))
                set_state_dimensions(dims, 'outputs', (self.get_output_dimensions()[1],))
            elif self.grid_shape == 'unequal':
                self.info['num_actions'] = 2  # increment twice for unequal grid shape
                set_state_dimensions(dims, 'env', self.get_env_dimensions())
                set_state_dimensions(dims, 'inputs', self.get_input_dimensions())
                set_state_dimensions(dims, 'outputs', self.get_output_dimensions())
            state['inputs']['dims']=dims

        if 'cells' in self.control_set:
            cells={}
            if 'env' in self.input_set:
                cells['env'] = self.env
                dims = self.get_env_dimensions()
                self.info['env'] = dims
                self.info['num_actions'] += dims[0]*dims[1]

            if 'inputs' in self.input_set:
                cells['inputs'] = self.get_array(self.dataset, self.index, 'input')

            if 'outputs' in self.input_set:
                cells['outputs'] = self.get_array(self.dataset, self.index, 'output')
            state['inputs']['cells']=cells

        return state, self.info

    def fitness_function_arrays(self, output_array, env_array):
        # First metric: square of the difference between the dimensions
        dim_metric = (env_array.shape[0] - output_array.shape[0]) ** 2 + (env_array.shape[1] - output_array.shape[1]) ** 2


        if 'cells' in self.control_set :
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
        if 'dims' in self.control_set and len(self.control_set) == 1:
            final_metric = dim_metric
        else:
            final_metric = dim_metric + element_metric

        return final_metric

    def fitness_function(self):
        output_array = np.array(self.arc_dict[self.dataset][self.index]['output'])
        env_array = self.env
        return self.fitness_function_arrays(output_array, env_array)

    def get_input(self, dataset):
        return np.array(self.arc_dict[dataset][self.index]['input'])

    def get_output(self, dataset):
        return np.array(self.arc_dict[dataset][self.index]['output'])

    def get_num_elements(self, dataset, array_key):
        return np.array(self.arc_dict[dataset][self.index][array_key]).size

    def get_info(self):
        return self.info

    def determine_grid_shape(self):
        output_dims = [np.array(task['output']).shape for task in self.arc_dict['train']]
        input_dims = [np.array(task['input']).shape for task in self.arc_dict['train']]

        if len(set(output_dims)) == 1:
            if len(set(input_dims)) == 1 and output_dims[0] == input_dims[0]:
                return None
            return 'equal'
        return 'unequal'
    

    def get_env_inputs_names(self):
        input_names = []
        dfactor = 1 if self.grid_shape == 'equal' else 2
        if 'dims' in self.control_set:
            if 'env' in self.input_set:
                input_names.append('IWE')
                if dfactor ==2 : input_names.append('IHE')
            if 'inputs' in self.input_set:
                input_names.append('IWI')
                if dfactor ==2 : input_names.append('IHI')
            if 'outputs' in self.input_set:
                input_names.append('IW0')
                if dfactor ==2 : input_names.append('IHO')

        if 'env' in self.info:
            dims = self.info['env']
            num = dims[0]*dims[1]
            for i in range(num):
                input_names.append(f'IE{i+1:03}')
            
        if 'inputs' in self.info:
            dims = self.info['inputs']
            num = dims[0]*dims[1]
            for i in range(num):
                input_names.append(f'II{i+1:03}')

        if 'outputs' in self.info:
            dims = self.info['outputs']
            num = dims[0]*dims[1]
            for i in range(num):
                input_names.append(f'IO{i+1:03}')
            
        return input_names



    def get_env_inputs_indexes(self):
        ninputs = 0

        if 'dims' in self.info:
            ninputs += self.info['dims']

        if 'env' in self.info:
            ninputs += self.info['env'][0]*self.info['env'][1]

        if 'inputs' in self.info:
            ninputs += self.info['inputs'][0]*self.info['inputs'][1]

        if 'outputs' in self.info:
            ninputs += self.info['outputs'][0]*self.info['outputs'][1]

        env_inputs_indexes = [i for i in range(ninputs)]

        return env_inputs_indexes

    def get_env_array(self):
        return self.env



# %% ../nbs/15_arc.ipynb 9
class ARCEnv(gym.Env):
    def __init__(self):
        super(ARCEnv, self).__init__()
        self.index = 0
        self.env = None
        self.dimensions = []
        self._fitness = 10000  # Initialize fitness to 10000
        self.state = []
        self.done = False

        # Class variables
        self.dataset = None

        # Render settings
        self.screen_width = 1000
        self.screen_height = 500
        self.cell_size = 30
        self.left_pad = 20
        self.height_pad = 20
        self.grid_down = 50
        self.symbol_down = 150
        self.screen = None
        self.isopen = True

        self.cmap = colors.ListedColormap(['#000000', '#0074D9', '#FF4136', '#2ECC40', '#FFDC00',
                                           '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25'])
        self.norm = colors.Normalize(vmin=0, vmax=9)

        self.fitness_label_font_size = 20
        self.fitness_value_font_size = 50

        self.iteration = 1  # Initialize iteration to 1
        self.code = ""  # Example property, ensure to set self.code elsewhere in your class
        self.data = None  # Placeholder for data
        self.arc_data = None  # Placeholder for ARCDataProcessor
        self.num_actions = 0  # Initialize num_actions

    def initialise(self, properties, arc_dict):
        """
        Initialize the environment with properties and arc_dict.
        """
        self.dataset = properties.get('dataset', None)
        self.arc_data = ARCDataProcessor(properties, arc_dict)
        self.reset()

    def step(self, actions):
        """
        Take a step in the environment.
        """
        self.arc_data.apply_actions(actions)

        if self.dataset == 'train':
            self.fitness = self.arc_data.fitness_function()

        self.state, self.info = self.arc_data.get_state()
        
        self.iteration += 1  # Increment iteration
        return self.state, self.fitness, self.done, self.info

    def reset(self):
        """
        Reset the environment to the initial state.
        """
        self.arc_data.reset()
        if self.dataset == 'train':
            self.fitness = self.arc_data.fitness_function()
        else:
            self.fitness = 10000  # or some default value
        self.done = False
        self.state, self.info = self.arc_data.get_state()
        self.iteration = 1  # Reset iteration
        self.num_actions = self.info['num_actions']  # Set num_actions

    def next(self):
        """
        Move to the next state in arc_dict.
        """
        return self.arc_data.next()

    def get_num_actions(self):
        """
        Get the number of actions.
        """
        return self.num_actions

    def get_env_inputs_names(self):
        """
        Get the environment input names.
        """
        return self.arc_data.get_env_inputs_names()

    def get_env_inputs_indexes(self):
        """
        Get the environment input indexes.
        """
        return self.arc_data.get_env_inputs_indexes()

    def set_dataset(self, dataset):
        """
        Set the dataset and update the value in arc_data.
        """
        self.dataset = dataset
        self.arc_data.set_dataset(dataset)

    def call_fitness_function_arrays(self):
        """
        Call fitness_function_arrays on arc_data.
        """
        return self.arc_data.fitness_function_arrays()

    def get_env_array(self):
        """
        Get the environment array from arc_data.
        """
        return self.arc_data.get_env_array()

    @property
    def fitness(self):
        """
        Get the current fitness value.
        """
        return self._fitness

    @fitness.setter
    def fitness(self, value):
        """
        Set the current fitness value.
        """
        self._fitness = value

    def render(self, mode='human'):
        """
        Render the environment using Pygame.
        """
        def draw_grid(screen, grid, top_left_x, top_left_y, cell_size):
            for i, row in enumerate(grid):
                for j, value in enumerate(row):
                    if top_left_x + j * cell_size < self.screen_width and top_left_y + i * cell_size < self.screen_height:
                        color = self.cmap(self.norm(value))[:3]  # Get RGB only, excluding alpha
                        color = tuple(int(c * 255) for c in color)  # Multiply each element by 255
                        pygame.draw.rect(screen, color, (top_left_x + j * cell_size, top_left_y + i * cell_size, cell_size, cell_size))
                        pygame.draw.rect(screen, (255, 255, 255), (top_left_x + j * cell_size, top_left_y + i * cell_size, cell_size, cell_size), 1)
            # Draw a black line around the grid
            if top_left_x < self.screen_width and top_left_y < self.screen_height:
                pygame.draw.rect(screen, (0, 0, 0), (top_left_x, top_left_y, cell_size * len(grid[0]), cell_size * len(grid)), 2)

        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption('ARC Environment')

        input_grid = np.array(self.arc_data.get_input(self.dataset))
        output_grid = np.array(self.arc_data.get_output(self.dataset))
        env_grid = self.arc_data.env

        # Top left coordinates
        input_grid_x = self.left_pad
        input_grid_y = self.grid_down
        arrow_img_x = input_grid_x + input_grid.shape[1] * self.cell_size + self.left_pad
        arrow_img_y = self.symbol_down
        output_grid_x = arrow_img_x + 50 + self.left_pad
        output_grid_y = self.grid_down
        equals_img_x = output_grid_x + output_grid.shape[1] * self.cell_size + self.left_pad
        equals_img_y = self.symbol_down
        env_grid_x = equals_img_x + 50 + self.left_pad
        env_grid_y = self.grid_down
        fitness_text_x = env_grid_x + env_grid.shape[1] * self.cell_size + self.left_pad
        fitness_text_y = self.grid_down + self.height_pad
        fitness_value_y = fitness_text_y + self.fitness_label_font_size + self.height_pad
        tick_cross_y = fitness_value_y + self.fitness_value_font_size + self.height_pad
        table_y = self.grid_down + max(input_grid.shape[0], output_grid.shape[0], env_grid.shape[0]) * self.cell_size + self.height_pad

        # Adjust screen size if necessary
        if fitness_text_x + self.fitness_value_font_size > self.screen_width:
            self.screen_width = fitness_text_x + self.fitness_value_font_size + self.left_pad
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        if env_grid_y + env_grid.shape[0] * self.cell_size > self.screen_height:
            self.screen_height = env_grid_y + env_grid.shape[0] * self.cell_size + self.height_pad
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.screen.fill((255, 255, 255))  # Clear the screen

        draw_grid(self.screen, input_grid, input_grid_x, input_grid_y, self.cell_size)
        draw_grid(self.screen, output_grid, output_grid_x, output_grid_y, self.cell_size)
        draw_grid(self.screen, env_grid, env_grid_x, env_grid_y, self.cell_size)

        # Load and scale images
        arrow_img = pygame.transform.scale(pygame.image.load('images/arrow.png'), (50, 50))
        equals_img = pygame.transform.scale(pygame.image.load('images/equals.jpg'), (50, 50))
        green_tick_img = pygame.transform.scale(pygame.image.load('images/green_tick.png'), (50, 50))
        red_cross_img = pygame.transform.scale(pygame.image.load('images/red-cross.png'), (50, 50))

        if arrow_img_x < self.screen_width and arrow_img_y < self.screen_height:
            self.screen.blit(arrow_img, (arrow_img_x, arrow_img_y))
        if equals_img_x < self.screen_width and equals_img_y < self.screen_height:
            self.screen.blit(equals_img, (equals_img_x, equals_img_y))

        # Display fitness text
        label_font = pygame.font.Font(None, self.fitness_label_font_size)
        value_font = pygame.font.Font(None, self.fitness_value_font_size)
        label_font.set_bold(True)
        fitness_label = label_font.render("Fitness:", True, (0, 0, 0))
        fitness_value = value_font.render(f"{self.fitness:.2f}", True, (0, 0, 0))
        if fitness_text_x < self.screen_width and fitness_text_y < self.screen_height:
            self.screen.blit(fitness_label, (fitness_text_x, fitness_text_y))
        if fitness_text_x < self.screen_width and fitness_value_y < self.screen_height:
            self.screen.blit(fitness_value, (fitness_text_x, fitness_value_y))

        if self.fitness < 1e-6:
            if fitness_text_x < self.screen_width and tick_cross_y < self.screen_height:
                self.screen.blit(green_tick_img, (fitness_text_x, tick_cross_y))
        else:
            if fitness_text_x < self.screen_width and tick_cross_y < self.screen_height:
                self.screen.blit(red_cross_img, (fitness_text_x, tick_cross_y))

        # Draw table with Code, Iteration, and Index
        table_font = pygame.font.Font(None, 24)
        table_labels = ["Code", "Iteration", "Index"]
        table_values = [os.path.splitext(self.code)[0], self.iteration, self.arc_data.index]  # Display code without file extension
        table_x = self.left_pad
        table_y = table_y

        for i, (label, value) in enumerate(zip(table_labels, table_values)):
            label_surface = table_font.render(label, True, (0, 0, 0))
            value_surface = table_font.render(str(value), True, (0, 0, 0))
            self.screen.blit(label_surface, (table_x + i * 200, table_y))
            self.screen.blit(value_surface, (table_x + i * 200, table_y + 30))

        pygame.display.flip()

    def close(self):
        """
        Close the environment, save the screen to an HTML and an image file.
        """
        if self.screen is not None:
            os.makedirs("c:/tmp/arc/", exist_ok=True)
            pygame.image.save(self.screen, "c:/tmp/arc/screen_image.png")
            
            # Save the screen image to an HTML format
            with open("c:/tmp/arc/screen_image.html", "w") as f:
                f.write(f"<html><body><img src='screen_image.png'></body></html>")

            pygame.display.quit()
            pygame.quit()
            self.isopen = False


