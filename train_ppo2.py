# Copyright 2019 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

# make sure gym is loaded
import gym
import gym_scaling

from baselines import deepq
from baselines.common import models
from baselines.common.vec_env import DummyVecEnv
from baselines.ppo2 import ppo2
from gym_scaling.envs.scaling_env import INPUTS
import numpy as np


def makeEnv():
    return gym.make('Scaling-v0')


def main():
    vecEnv = DummyVecEnv([makeEnv])
    env = vecEnv.envs[0]
    model = ppo2.learn(
        network=models.mlp(num_hidden=20, num_layers=1),
        env=vecEnv,
        total_timesteps=1000000
    )

    # play model using shorter change rate
    env.change_rate = 100

    play(env, model, 1000)

    # play sine curve
    env.change_rate = 1
    env.scaling_env_options['input'] = INPUTS['SINE_CURVE']

    play(env, model, 1000)

    env.close()


def play(env, model, frames):
    print("Running trained model")
    obs = env.reset()
    state = model.initial_state if hasattr(model, 'initial_state') else None
    dones = np.zeros((1,))
    while frames > 0:
        frames = frames - 1
        if state is not None:
            actions, _, state, _ = model.step(obs, S=state, M=dones)
        else:
            actions, _, _, _ = model.step(obs)

        obs, _, done, _ = env.step(actions[0])
        env.render()
        done = done.any() if isinstance(done, np.ndarray) else done
        if done:
            obs = env.reset()


if __name__ == '__main__':
    main()
