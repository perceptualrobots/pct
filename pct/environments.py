# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05_environments.ipynb (unless otherwise specified).

__all__ = ['EnvironmentFactory', 'OpenAIGym', 'CartPoleV1', 'CartPoleDV1', 'PendulumV0', 'PendulumV0_1',
           'MountainCarV0', 'MountainCarContinuousV0', 'VelocityModel', 'DummyModel', 'EnvironmentFactory']

# Cell
import gym
import math
import numpy as np
import pct.putils as vid
from .functions import BaseFunction

# Cell
class EnvironmentFactory:
    factories = {}
    def addFactory(id, environmentFactory):
        EnvironmentFactory.factories.put[id] = environmentFactory
    addFactory = staticmethod(addFactory)
    # A Template Method:
    def createEnvironment(id):
        if not EnvironmentFactory.factories.__contains__(id):
            EnvironmentFactory.factories[id] = \
              eval(id + '.Factory()')
        return EnvironmentFactory.factories[id].create()
    createEnvironment = staticmethod(createEnvironment)

# Cell
class OpenAIGym(BaseFunction):
    "A function that creates an runs an environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    def __init__(self, env_name=None, render=False, video_wrap=False, value=0, name="gym",
                 seed=None, links=None, new_name=True, early_termination=False, **cargs):
        super().__init__(name, value, links, new_name)
        self.early_termination=early_termination
        self.video_wrap = video_wrap
        self.env_name=env_name
        self.max_episode_steps=4000
        self.create_env(seed)
        self.render = render
        self.reward = 0
        self.done = False
        self.info = {}

    def __call__(self, verbose=False):
        super().check_links(1)
        self.early_terminate()
        self.input = self.links[0].get_value()
        self.process_input()
        self.obs = self.env.step(self.input)

        self.value = self.obs[0]
        self.reward = self.obs[1]
        self.done = self.obs[2]
        self.info = self.obs[3]

        self.process_values()
        out = super().__call__(verbose)

        if self.render:
            self.env.render()

        return out


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

    def reset(self, full=True):
        if full:
            super().reset()
        else:
            self.value=0
        self.really_done = False
        return self.env.reset()


    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()
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
        genv = gym.make(self.env_name)
        genv._max_episode_steps = self.max_episode_steps
        if self.video_wrap:
            self.env =  vid.wrap_env(genv)
        else:
            self.env = genv
        self.env.seed(seed)
        self.env.reset()

    def set_seed(self, seed):
        self.env.seed(seed)


    def close(self):
        self.env.close()

    class Factory:
        def create(self): return OpenAIGym()

# Cell
class CartPoleV1(OpenAIGym):
    "A function that creates an runs the CartPole-v1 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 1 cart_velocity
    # 0 cart_position
    # 3 pole_velocity
    # 2 pole_angle
    def __init__(self, render=False, video_wrap=False, value=0, name="CartPole-v1",
                 seed=None, links=None, new_name=True, **cargs):
        super().__init__('CartPole-v1', render, video_wrap, value, name, seed, links, new_name, **cargs)

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
        def create(self): return CartPoleV1()


# Cell
class CartPoleDV1(OpenAIGym):
    "A function that creates an runs the CartPole-v1 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 1 cart_velocity
    # 0 cart_position
    # 3 pole_velocity
    # 2 pole_angle
    def __init__(self, render=False, video_wrap=False, value=0, name="CartPoleD-v1",
                 seed=None, links=None, new_name=True, **cargs):
        super().__init__('CartPoleD-v1', render, video_wrap, value, name, seed, links, new_name, **cargs)

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
        def create(self): return CartPoleDV1()

# Cell
class PendulumV0(OpenAIGym):
    "A function that creates an runs the Pendulum-v0 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 0 cos(theta) - +1 is up, -1 is down, 0 is left and right
    # 1 sin(theta) - +1 is left, -1 is right, 0 is up and down
    # 2 theta dot - +dot is anti-clockwise, -dot is clockwise
    # 3 theta +pi/-pi (added here) 0 is pointing upwards, +pi is anti-clockwise, -pi is clockwise
    # 4 theta +x+pi/x-pi (added here) 0 is pointing downwards, + is anti-clockwise, - is clockwise
    # reward - -(theta^2 + 0.1*theta_dt^2 + 0.001*action^2)

    def __init__(self, render=False, video_wrap=False, value=0, name="Pendulum-v0",
                 seed=None, links=None, new_name=True, **cargs):
        super().__init__('Pendulum-v0', render, video_wrap, value, name, seed, links, new_name, **cargs)

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
        def create(self): return PendulumV0()


# Cell
class PendulumV0_1(OpenAIGym):
    "A function that creates an runs the Pendulum-v0 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 0 cos(theta) - +1 is up, -1 is down, 0 is left and right
    # 1 sin(theta) - +1 is left, -1 is right, 0 is up and down
    # 2 theta dot - +dot is anti-clockwise, -dot is clockwise
    # 3 theta dot - normalised to +/- 1
    # 4 theta +1/-1 (added here) 1 is pointing upwards, + is anti-clockwise, - is clockwise
    # reward - -(theta^2 + 0.1*theta_dt^2 + 0.001*action^2)

    def __init__(self, render=False, video_wrap=False, value=0, name="Pendulum-v0-1",
                 seed=None, links=None, new_name=True, **cargs):
        super().__init__('Pendulum-v0', render, video_wrap, value, name, seed, links, new_name, **cargs)

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
        def create(self): return PendulumV0_1()

# Cell
class MountainCarV0(OpenAIGym):
    "A function that creates and runs the MountainCar-v0 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 0 Car position - -1.2 to +0.6, reference 0.45
    # 1 Car Velocity - -0.07 t0 +0.07
    # 2 Car position - 0 to +1.8, reference 1.65

    def __init__(self, render=False, video_wrap=False, value=0, name="MountainCarV0",
                 seed=None, links=None, new_name=True, **cargs):
        super().__init__('MountainCar-v0', render, video_wrap, value, name, seed, links, new_name, **cargs)

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
        def create(self): return MountainCarV0()


# Cell
class MountainCarContinuousV0(OpenAIGym):
    "A function that creates and runs the MountainCarContinuous-v0 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # 0 Car position - -1.2 to +0.6, reference 0.45
    # 1 Car Velocity - -0.07 t0 +0.07
    # 2 Car position - 0 to +1.8, reference 1.65

    def __init__(self, render=False, video_wrap=False, value=0, name="MountainCarContinuousV0",
                 seed=None, links=None, new_name=True, early_termination=True, **cargs):
        super().__init__('MountainCarContinuous-v0', render, video_wrap, value, name, seed, links,
                         new_name, early_termination, **cargs)
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
        def create(self): return MountainCarContinuousV0()


# Cell
class VelocityModel(BaseFunction):
    "A simple model of a moving object of a particular mass. Parameters: The environment name, mass. Links: Link to the action function."
    # from obs[0], indices

    def __init__(self, mass=50, value=0, name="VelocityModel", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)
        self.mass = mass

    def __call__(self, verbose=False):
        super().check_links(1)
        force = self.links[0].get_value()

        self.value = self.value + force / self.mass
        return super().__call__(verbose)

    def summary(self):
        super().summary("")

    def get_config(self):
        config = super().get_config()
        config["mass"] = self.mass

        return config

    def set_seed(self, seed):
        pass

    class Factory:
        def create(self): return VelocityModel()

# Cell
class DummyModel(BaseFunction):
    def __init__(self, name="World", links=None, new_name=True, **cargs):
        super().__init__(name, 0, links, new_name)

    def __call__(self, verbose=False):
        pass

    def summary(self):
        super().summary("")

    def get_config(self):
        pass

    class Factory:
        def create(self): return DummyModel()

# Cell
class EnvironmentFactory:
    factories = {}
    def addFactory(id, environmentFactory):
        EnvironmentFactory.factories.put[id] = environmentFactory
    addFactory = staticmethod(addFactory)

    # A Template Method:
    def createEnvironment(id):
        if not EnvironmentFactory.factories.__contains__(id):
            EnvironmentFactory.factories[id] = \
              eval(id + '.Factory()')
        return EnvironmentFactory.factories[id].create()

    createEnvironment = staticmethod(createEnvironment)

