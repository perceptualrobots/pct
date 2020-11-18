# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05_environments.ipynb (unless otherwise specified).

__all__ = ['OpenAIGym', 'PendulumV0']

# Cell
import gym
import math
import numpy as np
from .functions import BaseFunction

# Cell
class OpenAIGym(BaseFunction):
    "A function that creates an runs an environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    def __init__(self, env_name=None, render=False, video_wrap=False, value=0, name="gym", links=None, new_name=True, **cargs):
        super().__init__(name, value, links, new_name)

        self.video_wrap = video_wrap
        self.env_name=env_name
        self.create_env(env_name, 4000)
        self.render = render
        self.reward = 0
        self.done = False
        self.info = {}

    def __call__(self, verbose=False):
        super().check_links(1)
        input = self.links[0].get_value()
        if input == 1 or input == -1 or input == 0:
            obs = self.env.step(input)
        else:
            raise Exception(f'OpenAIGym: Input value of {input} is not valid, must be 1,0 or -1.')

        # from obs[0], indices
        # 1 cart_velocity
        # 0 cart_position
        # 3 pole_velocity
        # 2 pole_angle

        self.value = obs[0]
        if self.name == 'CartPole-v1':
            self.value = np.append(self.value, obs[0][0]+math.sin(obs[0][2]))

        self.reward = obs[1]
        self.done = obs[2]
        self.info = obs[3]

        if self.render:
            self.env.render()

        return super().__call__(verbose)

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


    def create_env(self, env_name, max_episode_steps):
        genv = gym.make(env_name)
        genv._max_episode_steps = max_episode_steps
        if self.video_wrap:
            self.env =  vid.wrap_env(genv)
        else:
            self.env = genv
            self.env.reset()

    def close(self):
        self.env.close()

# Cell
class PendulumV0(OpenAIGym):
    "A function that creates an runs an environment from OpenAI Gym. Parameter: The environment name. Flag to display environment. Links: Link to the action function."
    def __init__(self, render=False, video_wrap=False, value=0, name="gym", links=None, new_name=True, **cargs):
        env_name= 'Pendulum-v0'
        super().__init__(env_name, render, video_wrap, value, name, links, new_name, **cargs)


    # from obs[0], indices
    # 0 cos(theta)
    # 1 sin(theta)
    # 2 theta dot
    # 3 theta +pi/-pi (added here)
    # reward - -(theta^2 + 0.1*theta_dt^2 + 0.001*action^2)

    def __call__(self, verbose=False):
        super().__call__(verbose)

        pi = math.copysign(math.acos(obs[0][0]), obs[0][1])
        self.value = np.append(self.value, pi)

