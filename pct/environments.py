# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05_environments.ipynb (unless otherwise specified).

__all__ = ['OpenAIGym', 'CartPoleV1', 'PendulumV0', 'VelocityModel']

# Cell
import gym
import math
import numpy as np
from .functions import BaseFunction

# Cell
class OpenAIGym(BaseFunction):
    "A function that creates an runs an environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    def __init__(self, env_name=None, render=False, video_wrap=False, value=0, name="gym",
                 seed=None, links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)

        self.video_wrap = video_wrap
        self.env_name=env_name
        self.create_env(env_name, 4000, seed)
        self.render = render
        self.reward = 0
        self.done = False
        self.info = {}

    def __call__(self, verbose=False):
        super().check_links(1)
        self.input = self.links[0].get_value()
        self.process_input()
        self.obs = self.env.step(self.input)

        self.value = self.obs[0]
        self.reward = self.obs[1]
        self.done = self.obs[2]
        self.info = self.obs[3]

        if self.done:
            raise Exception(f'1000: OpenAIGym Env: {self.env_name} has terminated.')


        if self.render:
            self.env.render()

        return super().__call__(verbose)

    def process_input(self):
        pass

    def reset(self):
        super().reset()
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


    def create_env(self, env_name, max_episode_steps, seed):
        genv = gym.make(env_name)
        genv._max_episode_steps = max_episode_steps
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

# Cell
class CartPoleV1(OpenAIGym):
    "A function that creates an runs the CartPole-v1 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 1 cart_velocity
    # 0 cart_position
    # 3 pole_velocity
    # 2 pole_angle
    def __init__(self, env_name='CartPole-v1', render=False, video_wrap=False, value=0, name="gym",
                 seed=None, links=None, new_name=True, **cargs):
        super().__init__(env_name, render, video_wrap, value, name, seed, links, new_name, **cargs)

    def __call__(self, verbose=False):
        super().__call__(verbose)

        self.value = np.append(self.value, self.obs[0][0]+math.sin(self.obs[0][2]))

        return self.value

    def process_input(self):
        if self.input<0:
            self.input=0
        elif self.input>0:
            self.input=1
        else:
            self.input=0



# Cell
class PendulumV0(OpenAIGym):
    "A function that creates an runs the Pendulum-v0 environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    # from obs[0], indices
    # 0 cos(theta)
    # 1 sin(theta)
    # 2 theta dot
    # 3 theta +pi/-pi (added here) zero is pointing upwards
    # reward - -(theta^2 + 0.1*theta_dt^2 + 0.001*action^2)

    def __init__(self, env_name='Pendulum-v0', render=False, video_wrap=False, value=0, name="gym",
                 seed=None, links=None, new_name=True, **cargs):
        super().__init__(env_name, render, video_wrap, value, name, seed, links, new_name, **cargs)

    def __call__(self, verbose=False):
        super().check_links(1)
        self.input = self.links[0].get_value()
        self.obs = self.env.step([self.input])

        self.value = self.obs[0]
        self.reward = self.obs[1]
        self.done = self.obs[2]
        self.info = self.obs[3]

        pi = math.copysign(math.acos(self.obs[0][0]), self.obs[0][1])
        self.value = np.append(self.value, pi)

        if self.render:
            self.env.render()

        if verbose :
            print(self.output_string())

        return self.value



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
