# Copyright 2019 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import random

import gym
import gym_scaling

from baselines import deepq
from baselines.common import models
from gym_scaling.envs.scaling_env import INPUTS


def main():
    random.seed(10)

    env = gym.make('Scaling-v0')
    act = deepq.learn(
        env,
        network=models.mlp(num_hidden=20, num_layers=1),
        train_freq=4,
        buffer_size=1000,
        exploration_fraction=1.0,
        exploration_final_eps=1e-5,
        total_timesteps=200000,
        prioritized_replay=True,
        checkpoint_freq=None,
        print_freq=1
    )

    # play model using shorter change rate
    env.change_rate = 100

    frames = 1000
    play(act, env, frames)

    # play sine curve
    env.change_rate = 1
    env.scaling_env_options['input'] = INPUTS['SINE_CURVE']

    play(act, env, frames)


def play(act, env, frames):
    try:
        obs = env.reset()
        while frames > 0:
            frames = frames - 1

            env.render()
            obs, _, _, _ = env.step(act(obs[None], stochastic=False)[0])

    except KeyboardInterrupt:
        env.close()
        raise KeyboardInterrupt


if __name__ == '__main__':
    main()
