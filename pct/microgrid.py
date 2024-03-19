# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/13_microgrid.ipynb.

# %% auto 0
__all__ = ['MicroGridEnvPlus']

# %% ../nbs/13_microgrid.ipynb 4
import random
import gym.spaces as spaces
import numpy as np
from drl_microgrid_ems.tcl_env_dqn import MicroGridEnv, DEFAULT_ITERATIONS, DEFAULT_NUM_TCLS, DEFAULT_NUM_LOADS, DEFAULT_PRICES, DEFAULT_TEMPERATURS, BASE_LOAD, PRICE_TIERS, Generation, Grid, MAX_GENERATION


# %% ../nbs/13_microgrid.ipynb 6
class MicroGridEnvPlus(MicroGridEnv):
    def __init__(self, **kwargs):
        """
        Overriding MicroGridEnv constructor.
        """
        seed = kwargs.get("seed", None)
        if seed:
            self.seed(seed)
        pass

    def initialise(self, properties=None, **kwargs):
        self.day0 = 1
        self.dayN = 10

        if 'day0' in properties:
            self.day0 = properties['day0']
        if 'dayN' in properties:
            self.dayN = properties['dayN']

        if 'initial_seed' in properties:
            random.seed(properties['initial_seed'])
        # Get number of iterations and TCLs from the 
        # parameters (we have to define it through kwargs because 
        # of how Gym works...)
        if 'iterations' in properties:
            self.iterations = properties['iterations']
        else:
            self.iterations = kwargs.get("iterations", DEFAULT_ITERATIONS)
        self.num_tcls = kwargs.get("num_tcls", DEFAULT_NUM_TCLS)
        self.num_loads = kwargs.get("num_loads", DEFAULT_NUM_LOADS)
        self.prices = kwargs.get("prices", DEFAULT_PRICES)
        self.temperatures = kwargs.get("temperatures", DEFAULT_TEMPERATURS)
        self.base_load = kwargs.get("base_load", BASE_LOAD)
        self.price_tiers = kwargs.get("price_tiers", PRICE_TIERS)

        # calculated here rather than repeatedly in _build_state
        self.temperatures_min = min(self.temperatures)
        self.temperatures_divisor = max(self.temperatures)-min(self.temperatures)

        self.day = None
        self.day_list = []
        if 'day_mode' in properties:
            self.day_mode = properties['day_mode']
        else:
            raise Exception('day_mode property for MicroGrid must be defined')
    
        if 'initial_day' in properties:
            self.day = properties['initial_day']
            self.set_day_list(mode=self.day_mode)
        else:
            self.day = random.randint(0,10)
            
        # The current timestep
        self.time_step = 0

        # The cluster of TCLs to be controlled.
        # These will be created in reset()
        self.tcls_parameters = []
        self.tcls = []
        # The cluster of loads.
        # These will be created in reset()
        self.loads_parameters = []
        self.loads = []

        self.generation = Generation(MAX_GENERATION)
        self.grid = Grid()

        # calculated here rather than repeatedly in _build_state
        self.grid_buy_prices_min = min(self.grid.buy_prices)
        self.grid_buy_prices_divisor = max(self.grid.buy_prices) - min(self.grid.buy_prices)

        for i in range(self.num_tcls):
            self.tcls_parameters.append(self._create_tcl_parameters())

        for i in range(self.num_loads):
            self.loads_parameters.append(self._create_load_parameters())

        self.action_space = spaces.Discrete(80)
        
        # Observations: A vector of TCLs SoCs + loads +battery soc+ power generation + price + temperature + time of day
        self.observation_space = spaces.Box(low=-100, high=100, dtype=np.float32, 
                    shape=(1  + 7,))


    def _build_state(self):
        """ 
        Return current state representation as one vector.
        Returns:
            state: 1D state vector, containing state-of-charges of all TCLs, Loads, current battery soc, current power generation,
                   current temperature, current price and current time (hour) of day
        """
        # SoCs of all TCLs binned + current temperature + current price + time of day (hour)
        socs = np.array([tcl.SoC for tcl in self.tcls])
        # Scaling between -1 and 1
        socs = (socs+np.ones(shape=socs.shape)*4)/(1+4)
        socs=np.average(socs)

        # loads = np.array([l.load(self.time_step) for l in self.loads])
        # loads = sum([l.load(self.time_step) for l in self.loads])
        # # Scaling loads
        # loads = (loads-(min(BASE_LOAD)+2)*DEFAULT_NUM_LOADS)/((max(BASE_LOAD)+4-min(BASE_LOAD)-2)*DEFAULT_NUM_LOADS)

        loads = BASE_LOAD[(self.time_step) % 24]
        loads = (loads - min(BASE_LOAD)) / (max(BASE_LOAD) - min(BASE_LOAD))


        current_generation = self.generation.current_generation(self.day+self.time_step)
        current_generation /= self.generation.max_capacity

        temperature = self.temperatures[self.day+self.time_step]
        temperature = (temperature-self.temperatures_min)/self.temperatures_divisor

        price = self.grid.buy_prices[self.day+self.time_step]
        price = (price - self.grid_buy_prices_min) / self.grid_buy_prices_divisor

        high_price = self.high_price/(4 * self.iterations)

        time_step = (self.time_step)/24

        state = np.array([socs, loads, high_price, self.battery.SoC, current_generation,
                         temperature,
                         price,
                         time_step])
        return state


    def reset(self,day=None):
        """
        Create new TCLs, and return initial state.
        Note: Overrides previous TCLs
        """
        if day==None:
            self.day = self.get_day()
        else:
            self.day = day

        # print("Day:",self.day)
        self.time_step = 0
        self.battery = self._create_battery()
        self.energy_sold = 0
        self.energy_bought = 0
        self.energy_generated = 0
        self.control=0
        self.sale_price = PRICE_TIERS[2]
        self.high_price = 0
        self.tcls.clear()
        # initial_tcl_temperature = random.normalvariate(12, 5)
        initial_tcl_temperature = 12

        for i in range(self.num_tcls):
            parameters = self.tcls_parameters[i]
            self.tcls.append(self._create_tcl(parameters[0],parameters[1],parameters[2],parameters[3],initial_tcl_temperature))

        self.loads.clear()
        for i in range(self.num_loads):
            parameters = self.loads_parameters[i]
            self.loads.append(self._create_load(parameters[0],parameters[1]))

        self.battery = self._create_battery()
        return self._build_state()


    def set_day_list(self, mode=None):
        if isinstance(mode, list):
            self.day_list =  mode.copy()
        else:
            self.day_list =  [ i for i in range(self.day0, self.dayN+1, 1)]
            if 'random' == mode:
                random.shuffle(self.day_list)

    def get_day(self):
        if len(self.day_list) == 0:
            self.set_day_list(self.day_mode)

        day = self.day_list[0]
        self.day_list.remove(day)

        return day



    

# %% ../nbs/13_microgrid.ipynb 7
#| export

  
