# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_environments.ipynb.

# %% auto 0
__all__ = ['EnvironmentFactory', 'ControlEnvironment', 'OpenAIGym', 'CartPoleV1', 'CartPoleDV1', 'Pendulum', 'MountainCarV0',
           'MountainCarContinuousV0', 'WindTurbine', 'VelocityModel', 'DummyModel', 'WebotsWrestler',
           'WebotsWrestlerSupervisor', 'Bridge']

# %% ../nbs/05_environments.ipynb 3
import gym
import math
import numpy as np
from abc import abstractmethod
import pct.putils as vid
from .functions import BaseFunction
from .putils import FunctionsList, SingletonObjects
from .network import ClientConnectionManager
from .webots import WebotsHelper
from .yaw_module import YawEnv

# %% ../nbs/05_environments.ipynb 4
class EnvironmentFactory:
    factories = {}
    def addFactory(id, environmentFactory):
        EnvironmentFactory.factories.put[id] = environmentFactory
    addFactory = staticmethod(addFactory)
    
    # A Template Method:
    def createEnvironment(id, seed=None):
        if not EnvironmentFactory.factories.__contains__(id):
            EnvironmentFactory.factories[id] = \
              eval(id + '.Factory()')
        return EnvironmentFactory.factories[id].create(seed=seed)
    
    createEnvironment = staticmethod(createEnvironment)       
    
    
    def createEnvironmentWithNamespace(sid, namespace=None, seed=None):
        id = sid + f'.FactoryWithNamespace()'                
        if not EnvironmentFactory.factories.__contains__(id):
            EnvironmentFactory.factories[id] = eval(id)
        return EnvironmentFactory.factories[id].create(namespace=namespace, seed=seed)
    createEnvironmentWithNamespace = staticmethod(createEnvironmentWithNamespace)

# %% ../nbs/05_environments.ipynb 5
class ControlEnvironment(BaseFunction):
    
    def __call__(self, verbose=False):
        super().check_links(self.num_links)
        self.early_terminate()
        self.process_inputs()
        self.process_actions()
        self.obs = self.apply_actions_get_obs()
        self.parse_obs()    
        self.process_values()
        out = super().__call__(verbose)
            
        return out 
    
    def get_parameters_list(self):
        return [self.name]    
            
    
    def get_reward(self):
        return self.reward
    
    def set_properties(self, props):
        "Set the properties on a paramter."
        if props is None:
            raise Exception(f'No environment properties provided. Should be empty rather than None.')

        if props != None:
            for key, value in props.items():
                setattr(self, key, value)
        

    @abstractmethod
    def reset(self, full=True, seed=None): 
        pass
    
    @abstractmethod
    def parse_obs(self):
        pass
               
    @abstractmethod
    def process_inputs(self):
        pass

#self.input = self.links[0].get_value()
        
    @abstractmethod
    def process_actions(self):
        pass

    @abstractmethod
    def apply_actions_get_obs(self):
        pass
    
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def set_render(self, render):
        pass


# %% ../nbs/05_environments.ipynb 6
class OpenAIGym(ControlEnvironment):
    "A function that creates an runs an environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    def __init__(self, env_name=None, render=False, render_mode= "rgb_array", video_wrap=False, value=0, name="gym", 
                 seed=None, links=None, new_name=True, early_termination=False, namespace=None, **cargs):
        super().__init__(name=name, value=value, links=links, new_name=new_name, namespace=namespace)
        self.render_mode=render_mode
        self.early_termination=early_termination
        self.video_wrap = video_wrap
        self.env_name=env_name
        self.max_episode_steps=4000
        if seed == None:
            raise Exception(f'Seed value for environment should be specified {self.__class__.__name__}:{env_name}.')
        self.create_env(seed)
        self.render = render
        self.reward = 0
        self.done = False
        self.info = {}
        self.num_links=1

    def __call__(self, verbose=False):
        out = super().__call__(verbose)
        
        if self.render:
            self.env.render()
            
        return out 

#     def __call__(self, verbose=False):
#         super().check_links(1)
#         self.early_terminate()
#         self.input = self.links[0].get_value()
#         self.process_input()
#         self.obs = self.env.step(self.input)
            
#         self.value = self.obs[0]
#         self.reward = self.obs[1]
#         self.done = self.obs[2]
#         self.info = self.obs[3]

#         self.process_values()
#         out = super().__call__(verbose)
        
#         if self.render:
#             self.env.render()
            
#         return out 

    def parse_obs(self):
        self.value = self.obs[0]
        self.reward = self.obs[1]
        self.done = self.obs[2]
        self.info = self.obs[3]
            
    def apply_actions_get_obs(self):
        return self.env.step(self.input)
    
    def set_video_wrap(self, video_wrap):
        self.video_wrap = video_wrap

        
    def early_terminate(self):
        if self.early_termination:
            if self.done:
                raise Exception(f'1000: OpenAIGym Env: {self.env_name} has terminated.')
    
    def process_inputs(self):
        raise Exception(f'Must be implemented in sub-class {self.__class__.__name__}:{self.env_name}.')

    def process_actions(self):
        raise Exception(f'Must be implemented in sub-class {self.__class__.__name__}:{self.env_name}.')
    
    def process_values(self):
        raise Exception(f'Must be implemented in sub-class {self.__class__.__name__}:{self.env_name}.')

    def set_render(self, render):
        self.render=render
        
    def reset(self, full=True, seed=None):        
        if seed == None:
            raise Exception(f'Seed value for environment should be specified {self.__class__.__name__}:{self.env_name}.')
        if full:
            super().reset()        
        else:
            self.value=0            
            self.check_links(len(self.links))
            for link in self.links:            
                link.set_value(0)
            
        self.really_done = False
        self.done = False
        return self.env.reset(seed=seed)


    def summary(self, extra=False):
        super().summary("", extra=extra)

    def get_config(self, zero=1):
        "Return the JSON  configuration of the function."
        config = {"type": type(self).__name__,
                    "name": self.name}
        
        if isinstance(self.value, np.ndarray):
            config["value"] = [i  * zero for i in self.value.tolist()]
        elif isinstance(self.value, list):
            config["value"] = [i  * zero for i in self.value]
        else:
            config["value"] = self.value * zero 
        
        ctr=0
        links={}
        for link in self.links:
            func = FunctionsList.getInstance().get_function(self.namespace, link)
            try:
                links[ctr]=func.get_name()
            except AttributeError:
                #raise Exception(f' there is no function called {link}, ensure it exists first.')            
                print(f'WARN: there is no function called {link}, ensure it exists first.')            
                links[ctr]=func
                
            ctr+=1
        
        config['links']=links

        config["env_name"] = self.env_name
        #config["values"] = self.value
        config["reward"] = round(self.reward,  self.decimal_places)
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

    
    def create_env(self, seed):
        genv = gym.make(self.env_name) #, render_mode=self.render_mode)
        genv._max_episode_steps = self.max_episode_steps
        if self.video_wrap:
            self.env =  vid.wrap_env(genv)
        else:
            self.env = genv
        self.env.reset(seed=seed)
        #self.env.seed(seed)
        #self.env.reset()
            
#     def set_seed(self, seed):
#         self.env.reset(seed=seed)
        #self.env.seed(seed)

    def get_graph_name(self):
        return super().get_graph_name() 
                

    def close(self):
        self.env.close()
        
    class Factory:
        def create(self): return OpenAIGym()
        
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return OpenAIGym(namespace=namespace, seed=seed)        

# %% ../nbs/05_environments.ipynb 7
class CartPoleV1(OpenAIGym):
    "A function that creates an runs the CartPole-v1 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 1 cart_velocity
    # 0 cart_position
    # 3 pole_velocity
    # 2 pole_angle
    def __init__(self, render=False, render_mode="rgb_array", video_wrap=False, value=0, name="CartPoleV1", 
                 seed=None, links=None, new_name=True, namespace=None, **cargs):
        super().__init__(env_name='CartPole-v1', render=render, render_mode=render_mode, video_wrap=video_wrap, value=value, name=name, seed=seed, 
                         links=links, new_name=new_name, namespace=namespace, **cargs)
 
    def __call__(self, verbose=False):
        super().__call__(verbose)
        
        return self.value
    
    def process_inputs(self):    
        self.input = self.links[0].get_value()    
    
    def process_actions(self):
        if self.input<0:
            self.input=0
        elif self.input>0:
            self.input=1
        else:
            self.input=0

    def process_values(self):
        self.value = np.append(self.value, self.obs[0][0]+math.sin(self.obs[0][2]))
                
    class Factory:
        def create(self, seed=None): return CartPoleV1(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return CartPoleV1(namespace=namespace, seed=seed)        

# %% ../nbs/05_environments.ipynb 8
class CartPoleDV1(OpenAIGym):
    "A function that creates an runs the CartPole-v1 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 1 cart_velocity
    # 0 cart_position
    # 3 pole_velocity
    # 2 pole_angle
    def __init__(self, render=False, render_mode="rgb_array", video_wrap=False, value=0, name="CartPoleD-v1", 
                 seed=None, links=None, new_name=True, namespace=None, **cargs):
        super().__init__('CartPoleD-v1', render=render, render_mode=render_mode, video_wrap=video_wrap, value=value, name=name, seed=seed, 
                         links=links, new_name=new_name, namespace=namespace, **cargs)
 
    def __call__(self, verbose=False):
        super().__call__(verbose)

        return self.value
    
    def process_values(self):
        self.value = np.append(self.value, self.obs[0][0]+math.sin(self.obs[0][2]))
        self.value = np.append(self.value, self.env.gravity)
    
    def process_actions(self):
        if self.input<0:
            self.input=0
        elif self.input>0:
            self.input=1
        else:
            self.input=0

    class Factory:
        def create(self, seed=None): return CartPoleDV1(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return CartPoleDV1(namespace=namespace, seed=seed)        

# %% ../nbs/05_environments.ipynb 9
class Pendulum(OpenAIGym):
    "A function that creates an runs the Pendulum-v1 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 0 cos(theta) - +1 is up, -1 is down, 0 is left and right
    # 1 sin(theta) - +1 is left, -1 is right, 0 is up and down
    # 2 theta dot - +dot is anti-clockwise, -dot is clockwise
    # New parameters:
    # 3 theta +pi/-pi (added here) 0 is pointing upwards, +pi is anti-clockwise, -pi is clockwise
    # deprecated 4 theta +x+pi/x-pi (added here) 0 is pointing downwards, + is anti-clockwise, - is clockwise
    # from obs[1]
    # reward - -(theta^2 + 0.1*theta_dt^2 + 0.001*action^2)

    def __init__(self, render=False, render_mode="rgb_array", video_wrap=False, value=0, name="Pendulum", 
                 seed=None, links=None, new_name=True, namespace=None,**cargs):        
        super().__init__('Pendulum-v1', render=render, render_mode=render_mode, video_wrap=video_wrap, value=value, name=name, seed=seed, 
                         links=links, new_name=new_name, namespace=namespace, **cargs)
        
        
    def __call__(self, verbose=False):        
        super().__call__(verbose)
                
        return self.value

    def process_inputs(self):
        self.input = self.links[0].get_value()
   
    def process_actions(self):
        pass
    
    def apply_actions_get_obs(self):
        return self.env.step([self.input])
        
    def parse_obs(self):    
        self.value = self.obs[0]
        self.reward = -self.obs[1]
        self.done = self.obs[2]
        self.info = self.obs[3]

    def process_values(self):
        th = math.copysign(math.acos(self.obs[0][0]), self.obs[0][1])
        self.value = np.append(self.value, th)
        
        if hasattr(self, 'reward_type'):
            dt = self.obs[0][2]
            if self.reward_type == 'surface1':
                # =afac*$B3*$B3+ bfac*$B3 /(badd+( C$2 * C$2)) + cfac*(PI()-ABS($B3))*(C$2 * C$2)
                self.reward = 0.5 *th*th+ 0.5*abs(th) /(0.2+( dt * dt)) + 0.001*(math.pi-abs(th))*(dt * dt)
            elif self.reward_type == 'surface2':            
                # = afac*POWER($B10*$B10, apow)+ bfac*POWER((ABS($B10) /(badd+( C$9 * C$9))), bpow) + cfac*POWER((PI()-ABS($B10))*(C$9 * C$9), cpow)
                self.reward = 0.5 *th*th+ 10*abs(th) /(5+( dt * dt)) + 0.05*(math.pi-abs(th))*(dt * dt)
            #print(f'PM: th {th:4.3} dt {dt:4.3} rew {self.reward:4.3}')

        pass

    

    class Factory:
        def create(self, seed=None): return Pendulum(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return Pendulum(namespace=namespace, seed=seed)                

# %% ../nbs/05_environments.ipynb 11
class MountainCarV0(OpenAIGym):
    "A function that creates and runs the MountainCar-v0 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 0 Car position - -1.2 to +0.6, reference 0.45 
    # 1 Car Velocity - -0.07 t0 +0.07
    # 2 Car position - 0 to +1.8, reference 1.65 
    
    def __init__(self, render=False, render_mode="rgb_array", video_wrap=False, value=0, name="MountainCarV0", 
                 seed=None, links=None, new_name=True, namespace=None, **cargs):        
        super().__init__('MountainCar-v0', render=render, render_mode=render_mode, video_wrap=video_wrap, value=value, name=name, seed=seed, 
                         links=links, new_name=new_name, namespace=namespace, **cargs)
        
    def __call__(self, verbose=False):        
        super().__call__(verbose)
                
        return self.value

    def process_inputs(self):
        self.input = self.links[0].get_value()

    def process_values(self):        
        self.reward = -self.obs[1]
        pos = self.value[0] + 1.2
        self.value = np.append(self.value, pos)

    def process_actions(self):
        if self.input<0:
            self.input=0
        elif self.input>0:
            self.input=2
        else:
            self.input=1

    class Factory:
        def create(self, seed=None): return MountainCarV0(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return MountainCarV0(namespace=namespace, seed=seed)                

# %% ../nbs/05_environments.ipynb 12
class MountainCarContinuousV0(OpenAIGym):
    "A function that creates and runs the MountainCarContinuous-v0 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # 0 Car position - -1.2 to +0.6, reference 0.45 
    # 1 Car Velocity - -0.07 t0 +0.07
    # 2 Car position - 0 to +1.8, reference 1.65 
    
    def __init__(self, render=False, render_mode="rgb_array", video_wrap=False, value=0, name="MountainCarContinuousV0", 
                 seed=None, links=None, new_name=True, early_termination=True, namespace=None, **cargs):        
        super().__init__('MountainCarContinuous-v0', render=render, render_mode=render_mode,  video_wrap=video_wrap, 
                         value=value, name=name, seed=seed, links=links, new_name=new_name, namespace=namespace,
                         early_termination=early_termination, **cargs)
        
        self.min_action = -1.0
        self.max_action = 1.0     
        self.really_done = False
        
    def __call__(self, verbose=False):        
        super().__call__(verbose)
                
        return self.value

    def early_terminate(self):
        if self.early_termination:
            if self.really_done:
                raise Exception(f'1000: OpenAIGym Env: {self.env_name} has terminated.')
            if self.done:
                self.reward = 0
                self.really_done = True

    def process_inputs(self):
        self.input = self.links[0].get_value()
                
    def process_actions(self):
        force = min(max(self.input, self.min_action), self.max_action)
        self.input=[force]
        
    def process_values(self):
        reward = self.obs[1]
        if reward > 90:
            reward = 0
        self.reward = - reward
        pos = self.value[0] + 1.2
        self.value = np.append(self.value, pos)

    class Factory:
        def create(self, seed=None): return MountainCarContinuousV0(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return MountainCarContinuousV0(namespace=namespace, seed=seed)               

# %% ../nbs/05_environments.ipynb 13
class WindTurbine(ControlEnvironment):
    "A function that creates and runs the YawEnv environment for a wind turbine. Indexes 0 - action, 1 - yaw error, 2 - wind direction, 3 - wind speed (ignore 0)."
    
    def __init__(self, value=0, name="WindTurbine", links=None, new_name=True, namespace=None, **cargs):        
        super().__init__(value=value, links=links, name=name, new_name=new_name, namespace=namespace, **cargs)
        
        self.num_links=1
        self.env_name='YawEnv'
        self.env = YawEnv()

        
    def __call__(self, verbose=False):        
        super().__call__(verbose)
                
        return self.value

    def set_properties(self, props):
        self.env.initialise(props)
        # wind_timeseries,start_index,stop_index,ancestors,filter_duration,yaw_parameters,

    def early_terminate(self):
        pass

    def process_inputs(self):
        self.input = self.links[0].get_value()
                
    def process_actions(self):
        if self.input < 0:
            self.action = 0
        elif self.input > 0:
            self.action = 2
        else:
            self.action = 1            
        
    
    def apply_actions_get_obs(self):
        return self.env.step(self.input)

    def parse_obs(self):
        self.value = self.obs[0][-1]
        self.reward = self.obs[2]
        self.done = self.obs[3]
        self.info = self.obs[4]

    def process_values(self):
        self.value = np.append(self.value, self.obs[1])
        pass
        # raise Exception(f'TBD {self.__class__.__name__}:{self.env_name}.')

    def get_config(self, zero=1):
        config = super().get_config(zero=zero)
        return config

    def get_graph_name(self):
        return super().get_graph_name() 
    
    def set_render(self, render):
        self.render=render
        
    def reset(self, full=True, seed=None):  
        self.env.reset()
        # raise Exception(f'TBD {self.__class__.__name__}:{self.env_name}.')

    def summary(self, extra=False):
        super().summary("", extra=extra)

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


    def close(self):
        self.env.close()

    class Factory:
        def create(self, seed=None): return WindTurbine(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return WindTurbine(namespace=namespace, seed=seed)        

# %% ../nbs/05_environments.ipynb 14
class VelocityModel(BaseFunction):
    "A simple model of a moving object of a particular mass. Parameters: The environment name, mass. Links: Link to the action function."
    # from obs[0], indices
    
    def __init__(self, mass=50, value=0, name="VelocityModel", links=None, 
                 num_links=1, new_name=True, indexes=0, namespace=None, **cargs):        
        super().__init__(name=name, value=value, links=links, new_name=new_name, namespace=namespace)
        self.mass = mass
        self.indexes=indexes
        self.num_links=num_links
        self.init_value()

    
    def __call__(self, verbose=False):
        super().check_links(self.num_links)
        force = self.links[0].get_value()

        if self.indexes>0:
            output = self.value[0] + force / self.mass
            self.value = [output for _ in range(self.indexes)]
        else:        
            self.value = self.value + force / self.mass
        return super().__call__(verbose)

    def init_value(self):
        if self.indexes>0:
            self.value = [1 for _ in range(self.indexes)]
        
        
    def reset(self, full=True, seed=None):
        if full:
            super().reset()        
        else:
            self.init_value()

        return True

    def set_render(self, render):
        pass
    
    def summary(self, extra=False):
        super().summary("", extra=extra)
        
    def get_parameters_list(self):
        return ['vm']    

    def get_config(self, zero=1):
        config = super().get_config(zero=zero)
        config["mass"] = self.mass
        
        return config

    def get_graph_name(self):
        return super().get_graph_name() 
    
#     def set_seed(self, seed):
#         pass

    class Factory:
        def create(self, seed=None): return VelocityModel(seed=seed)

# %% ../nbs/05_environments.ipynb 15
class DummyModel(BaseFunction):    
    def __init__(self, name="World", value=0, links=None, new_name=True, namespace=None, seed=None, **cargs):        
        super().__init__(name=name, value=value, links=links, new_name=new_name, namespace=namespace)
    
    def __call__(self, verbose=False):        
        pass

    def summary(self, extra=False):
        super().summary("", extra=extra)
    
    def get_config(self):
        pass

    def reset(self, full=True, seed=None):
        if full:
            super().reset()        
        else:
            self.init_value()

        return True

    def get_graph_name(self):
        return super().get_graph_name() 
    
    class Factory:
        def create(self, seed=None): return DummyModel(seed=seed)

# %% ../nbs/05_environments.ipynb 16
class WebotsWrestler(ControlEnvironment):
    "A function that creates and runs a Webots Wrestler robot."
    
    def __init__(self, render=False, value=0, name="WebotsWrestler", seed=None, links=None, new_name=True, 
                 early_termination=True, namespace=None):    
        super().__init__(name=name, value=value, links=links, new_name=new_name, namespace=namespace)
        self.early_termination=early_termination
        self.performance=0
        self.env_name='WebotsWrestler'
        self.reward = 0
        self.done = False
        self.rmode=1
        self.whelper = WebotsHelper(name=self.env_name, mode=self.rmode)
        self.num_links = self.whelper.get_num_links()
        self.initialised=False
        
        
    def initialise(self):
        init = {'msg': 'init', 'rmode': self.rmode}
        init.update(self.environment_properties)
        ClientConnectionManager.getInstance().send(init)
        self.obs = ClientConnectionManager.getInstance().receive()
        self.initialised=True

    def close(self):
        pass

    
    def send(self, data):
        ClientConnectionManager.getInstance().send(data)

    def receive(self):
        recv = ClientConnectionManager.getInstance().receive()
        #print(recv)
        return recv
                
    def __call__(self, verbose=False):     
            
        super().__call__(verbose)
                
        return self.value
    
    def early_terminate(self):
        if self.early_termination:
            if self.done:
                raise Exception(f'1001: Env: {self.env_name} has finished.')
                
    def process_inputs(self):
        #print('process_inputs')
        self.input = [ self.links[i].get_value() for i in range(0, len(self.links))]    
    
    def process_actions(self):
        self.actions = self.whelper.get_actions_dict(self.input)
        

    def apply_actions_get_obs(self):
        if not self.initialised:
            self.initialise()
            
        send={'msg': 'values', 'actions': self.actions}
        self.send(send)
        recv = self.receive()
        
        return recv

        
    def parse_obs(self):
        self.reward = self.obs['performance']
        if self.obs['msg']=='done':
            self.done=True
        
    def process_values(self):
        self.value = self.whelper.get_sensor_values(self.obs['sensors'])
        pass
    
    def summary(self, extra=False):
        super().summary("", extra=extra)
        
    def get_graph_name(self):
        return super().get_graph_name() 

    def get_config(self, zero=1):
        "Return the JSON  configuration of the function."
        config = {"type": type(self).__name__,
                    "name": self.name}
        
        if isinstance(self.value, np.ndarray):
            config["value"] = [i  * zero for i in self.value.tolist()]
        elif isinstance(self.value, list):
            config["value"] = [i  * zero for i in self.value]
        else:
            config["value"] = self.value * zero 
        
        ctr=0
        links={}
        for link in self.links:
            func = FunctionsList.getInstance().get_function(self.namespace, link)
            try:
                links[ctr]=func.get_name()
            except AttributeError:
                print(f'WARN: there is no function called {link}, ensure it exists first.')            
                links[ctr]=func
                
            ctr+=1
        
        config['links']=links

        config['env_name'] = self.env_name
        #config["values"] = self.value
        config['performance'] = round(self.reward, self.decimal_places)
        config['done'] = self.done
        #config['info'] = self.info
        
        return config

    def set_properties(self, props):
        self.environment_properties = props  

    
    
    def reset(self, full=True, seed=None): 
        self.reward = 0
        self.done = False
        self.initialised=False

    def set_render(self, render):
        pass
    
    class Factory:
        def create(self, seed=None): return WebotsWrestler(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return WebotsWrestler(namespace=namespace, seed=seed)          


# %% ../nbs/05_environments.ipynb 17
class WebotsWrestlerSupervisor(ControlEnvironment):
    "A function that creates and runs a Webots Wrestler robot."
    
    def __init__(self, render=False, value=0, name="WebotsWrestlerSupervisor", seed=None, links=None, new_name=True, 
                 early_termination=True, namespace=None):    
        super().__init__(name=name, value=value, links=links, new_name=new_name, namespace=namespace)
        self.early_termination=early_termination
#         from controllers.participant.participant import WrestlerSupervisor
#         SingletonObjects.getInstance().get_object('wrestler').initSupervisor()
        self.performance=0
        self.env_name='WebotsWrestlerSupervisor'
        self.reward = 0
        self.done = False
        self.rmode=1
        self.whelper = WebotsHelper(name=self.env_name, mode=self.rmode)
        self.num_links = self.whelper.get_num_links()
        self.initialised=False
        
        
    def initialise(self):
        SingletonObjects.getInstance().get_object('wrestler').initialise(self.environment_properties)
        self.initialised=True

    def close(self):
        pass
                    
    def __call__(self, verbose=False):     
            
        super().__call__(verbose)
                
        return self.value
    
    def early_terminate(self):
        if self.early_termination:
            if self.done:
                raise Exception(f'1001: Env: {self.env_name} has finished.')
                
    def process_inputs(self):
        #print('process_inputs')
        self.input = [ self.links[i].get_value() for i in range(0, len(self.links))]    
    
    def process_actions(self):
        self.actions = self.whelper.get_actions_dict(self.input)
        

    def apply_actions_get_obs(self):
        if not self.initialised:
            self.initialise()
            
        # do wrestler step here
        obs = SingletonObjects.getInstance().get_object('wrestler').rstep(self.actions)
        
        return obs

        
    def parse_obs(self):
        self.reward = self.obs['performance']
        self.done=self.obs['done']
        
    def process_values(self):
        self.value = self.whelper.get_sensor_values(self.obs['sensors'])
        pass
    
    def summary(self, extra=False):
        super().summary("", extra=extra)
        
    def get_graph_name(self):
        return super().get_graph_name() 

    def get_config(self, zero=1):
        "Return the JSON  configuration of the function."
        config = {"type": type(self).__name__,
                    "name": self.name}
        
        if isinstance(self.value, np.ndarray):
            config["value"] = [i  * zero for i in self.value.tolist()]
        elif isinstance(self.value, list):
            config["value"] = [i  * zero for i in self.value]
        else:
            config["value"] = self.value * zero 
        
        ctr=0
        links={}
        for link in self.links:
            func = FunctionsList.getInstance().get_function(self.namespace, link)
            try:
                links[ctr]=func.get_name()
            except AttributeError:
                print(f'WARN: there is no function called {link}, ensure it exists first.')            
                links[ctr]=func
                
            ctr+=1
        
        config['links']=links

        config['env_name'] = self.env_name
        #config["values"] = self.value
        config['performance'] = round(self.reward, self.decimal_places)
        config['done'] = self.done
        #config['info'] = self.info
        
        return config

    def set_properties(self, props):
        self.environment_properties = props  

    
    
    def reset(self, full=True, seed=None): 
        self.reward = 0
        self.done = False
        self.initialised=False


    def set_render(self, render):
        pass
    
    class Factory:
        def create(self, seed=None): return WebotsWrestlerSupervisor(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return WebotsWrestlerSupervisor(namespace=namespace, seed=seed)          
        

# %% ../nbs/05_environments.ipynb 18
class Bridge(ControlEnvironment):
    "An environment function with sensors set by external system."
    
    def __init__(self, render=False, value=0, name="Bridge", seed=None, links=None, new_name=True, 
                 early_termination=True, namespace=None):    
        super().__init__(name=name, value=value, links=links, new_name=new_name, namespace=namespace)
        self.early_termination=early_termination
        self.env_name='Bridge'
        self.reward = 0
        self.done = False
        self.mode=1
        
    def set_obs(self, obs):
        self.obs = obs
        self.value = obs
        
    def get_actions(self):
        self.input = [ self.links[i].get_value() for i in range(0, len(self.links))]    
        self.actions = self.input
        return self.actions
        
    def __call__(self, verbose=False):     
            
        super().__call__(verbose)
                
        return self.value
    
    def early_terminate(self):
        if self.early_termination:
            if self.done:
                raise Exception(f'1001: Env: {self.env_name} has finished.')
                
    def process_inputs(self):
        pass
    
    def process_actions(self):
        pass

    def apply_actions_get_obs(self):
        return None

    def set_value(self, value):
        for i in range(len(self.value)):
            self.value[i]= value
        
    def parse_obs(self):
        pass
    
    def process_values(self):
        pass
    
    def summary(self, extra=False):
        super().summary("", extra=extra)
        
    def get_graph_name(self):
        return super().get_graph_name() 

    def close(self):
        pass
    
    def get_config(self, zero=1):
        "Return the JSON  configuration of the function."
        config = {"type": type(self).__name__,
                    "name": self.name}
        
        if isinstance(self.value, np.ndarray):
            config["value"] = [i  * zero for i in self.value.tolist()]
        elif isinstance(self.value, list):
            config["value"] = [i  * zero for i in self.value]
        else:
            config["value"] = self.value * zero 
        
        ctr=0
        links={}
        for link in self.links:
            func = FunctionsList.getInstance().get_function(self.namespace, link)
            try:
                links[ctr]=func.get_name()
            except AttributeError:
                print(f'WARN: there is no function called {link}, ensure it exists first.')            
                links[ctr]=func
                
            ctr+=1
        
        config['links']=links
        config['env_name'] = self.env_name
        config['done'] = self.done
        
        return config
    
    def reset(self, full=True, seed=None): 
        self.done = False

    def set_render(self, render):
        pass
    
    class Factory:
        def create(self, seed=None): return Bridge(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return Bridge(namespace=namespace, seed=seed)          

