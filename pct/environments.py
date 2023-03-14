# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_environments.ipynb.

# %% auto 0
__all__ = ['EnvironmentFactory', 'ControlEnvironment', 'OpenAIGym', 'CartPoleV1', 'CartPoleDV1', 'Pendulum', 'Pendulum_1',
           'MountainCarV0', 'MountainCarContinuousV0', 'VelocityModel', 'DummyModel', 'WebotsWrestler']

# %% ../nbs/05_environments.ipynb 3
import gym
import math
import numpy as np
import pct.putils as vid
from .functions import BaseFunction
from .putils import FunctionsList
from .network import Client

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
        super().check_links(1)
        self.early_terminate()
        self.input = self.links[0].get_value()
        self.process_input()
        self.obs = self.get_obs(self.input)
            
        self.value = self.obs[0]
        self.reward = self.obs[1]
        self.done = self.obs[2]
        self.info = self.obs[3]

        self.process_values()
        out = super().__call__(verbose)
        
        if self.render:
            self.env.render()
            
        return out 
    

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

    def get_obs(self, input):
        return self.env.step(self.input)
    
    def set_video_wrap(self, video_wrap):
        self.video_wrap = video_wrap

        
    def early_terminate(self):
        if self.early_termination:
            if self.done:
                raise Exception(f'1000: OpenAIGym Env: {self.env_name} has terminated.')
    
    def process_input(self):
        pass
    
    def process_values(self):
        pass

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
            config["value"] = self.value.tolist() * zero
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
        config["reward"] = self.reward
        config["done"] = self.done
        config["info"] = self.info
        
        return config
    
    def get_reward(self):
        return self.reward

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
                
    def get_parameters_list(self):
        return [self.name]    
        
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
    
    def process_values(self):
        self.value = np.append(self.value, self.obs[0][0]+math.sin(self.obs[0][2]))
    
    def process_input(self):
        if self.input<0:
            self.input=0
        elif self.input>0:
            self.input=1
        else:
            self.input=0

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
                         links=links, new_name=new_name, **cargs)
 
    def __call__(self, verbose=False):
        super().__call__(verbose)

        return self.value
    
    def process_values(self):
        self.value = np.append(self.value, self.obs[0][0]+math.sin(self.obs[0][2]))
        self.value = np.append(self.value, self.env.gravity)
    
    def process_input(self):
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
    # 3 theta +pi/-pi (added here) 0 is pointing upwards, +pi is anti-clockwise, -pi is clockwise
    # 4 theta +x+pi/x-pi (added here) 0 is pointing downwards, + is anti-clockwise, - is clockwise
    # reward - -(theta^2 + 0.1*theta_dt^2 + 0.001*action^2)

    def __init__(self, render=False, render_mode="rgb_array", video_wrap=False, value=0, name="Pendulum", 
                 seed=None, links=None, new_name=True, namespace=None,**cargs):        
        super().__init__('Pendulum-v1', render=render, render_mode=render_mode, video_wrap=video_wrap, value=value, name=name, seed=seed, 
                         links=links, new_name=new_name, **cargs)
        
    def __call__(self, verbose=False):
        super().check_links(1)
        self.input = self.links[0].get_value()
        self.obs = self.env.step([self.input])
            
        self.value = self.obs[0]
        self.reward = -self.obs[1]
        self.done = self.obs[2]
        self.info = self.obs[3]
        
        pi = math.copysign(math.acos(self.obs[0][0]), self.obs[0][1])
        self.value = np.append(self.value, pi)
        #x = math.copysign(pi-abs(pi), pi)
        x = 10 + pi
        self.value = np.append(self.value, x)
        
        
        if self.render:
            self.env.render()
                
        if verbose :
            print(self.output_string())

        return self.value

    class Factory:
        def create(self, seed=None): return Pendulum(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return Pendulum(namespace=namespace, seed=seed)                

# %% ../nbs/05_environments.ipynb 10
class Pendulum_1(OpenAIGym):
    "A function that creates an runs the Pendulum-v1 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 0 cos(theta) - +1 is up, -1 is down, 0 is left and right
    # 1 sin(theta) - +1 is left, -1 is right, 0 is up and down
    # 2 theta dot - +dot is anti-clockwise, -dot is clockwise
    # 3 theta dot - normalised to +/- 1    
    # 4 theta +1/-1 (added here) 1 is pointing upwards, + is anti-clockwise, - is clockwise
    # reward - -(theta^2 + 0.1*theta_dt^2 + 0.001*action^2)

    def __init__(self, render=False, render_mode="rgb_array", video_wrap=False, value=0, name="Pendulum-1", 
                 seed=None, links=None, new_name=True, namespace=None,**cargs):        
        super().__init__('Pendulum-v1', render=render, render_mode=render_mode, video_wrap=video_wrap, value=value, name=name, seed=seed, 
                         links=links, new_name=new_name, **cargs)
        
    def __call__(self, verbose=False):
        super().check_links(1)
        self.input = self.links[0].get_value()
        self.obs = self.env.step([self.input])
            
        self.value = self.obs[0]
        self.reward = -self.obs[1]
        self.done = self.obs[2]
        self.info = self.obs[3]
        
        vel = self.obs[0][2]/8.0
        self.value = np.append(self.value, vel)
        x = math.copysign(math.acos(self.obs[0][0]), self.obs[0][1])/math.pi
        #theta = 100 - (10 * math.copysign(1-abs(x), x))
        theta = 100 - (10 * x)
        self.value = np.append(self.value, theta)
        
        if self.render:
            self.env.render()
                
        if verbose :
            print(self.output_string())

        return self.value

    class Factory:
        def create(self, seed=None): return Pendulum_1(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return Pendulum_1(namespace=namespace, seed=seed)                

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
                         links=links, new_name=new_name, **cargs)
        
    def __call__(self, verbose=False):        
        super().__call__(verbose)
                
        return self.value

    def process_values(self):        
        self.reward = -self.obs[1]
        pos = self.value[0] + 1.2
        self.value = np.append(self.value, pos)

    def process_input(self):
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
                         value=value, name=name, seed=seed, links=links, new_name=new_name, 
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
                
    def process_input(self):
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

# %% ../nbs/05_environments.ipynb 14
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

# %% ../nbs/05_environments.ipynb 15
class WebotsWrestler(ControlEnvironment):
    "A function that creates and runs a Webots Wrestler robot."
    
    def __init__(self, render=False, value=0, name="Wrestler", seed=None, links=None, new_name=True, 
                 early_termination=True, namespace=None):    
        super().__init__(name=name, value=value, links=links, new_name=new_name, namespace=namespace)
        self.early_termination=early_termination
        self.client = Client()
        init = {'msg': 'init'}
        self.client.put_dict(init)
        recv = self.client.get_dict()
        print(recv)
        self.done=False
        
        
    def __call__(self, verbose=False):        
        super().__call__(verbose)

        if self.done:
            send = {'msg': 'close'}
            self.client.put_dict(send)
            self.client.close()
        else:
            send = {'msg': 'values'}
            self.client.put_dict(send)
            recv = self.client.get_dict()
            print(recv)
                
        return self.value
    
    
    def get_obs(self, input):
        return self.env.step(self.input)


    def early_terminate(self):
        if self.early_termination:
            if self.done:
                self.reward = 0
                
    def process_input(self):
        print('process_input')
        
    def process_values(self):
        print('process_values')
#         reward = self.obs[1]
#         if reward > 90:
#             reward = 0
#         self.reward = - reward
#         pos = self.value[0] + 1.2
#         self.value = np.append(self.value, pos)

    def summary(self, extra=False):
        super().summary("", extra=extra)
        
    def get_graph_name(self):
        return super().get_graph_name() 

    def get_config(self, zero=1):
        "Return the JSON  configuration of the function."
        config = {"type": type(self).__name__,
                    "name": self.name}
        
        if isinstance(self.value, np.ndarray):
            config["value"] = self.value.tolist() * zero
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

        config["env_name"] = self.env_name
        #config["values"] = self.value
        config["performance"] = self.performance
        config["done"] = self.done
        config["info"] = self.info
    
    
    class Factory:
        def create(self, seed=None): return WebotsWrestler(seed=seed)
    class FactoryWithNamespace:
        def create(self, namespace=None, seed=None): return WebotsWrestler(namespace=namespace, seed=seed)          

