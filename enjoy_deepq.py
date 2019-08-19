# Copyright 2019 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import gym
import gym_scaling

from baselines import deepq
from baselines.common import models
from gym_scaling.envs.scaling_env import INPUTS
from train_deepq import play


def main():
    env = gym.make('Scaling-v0')
    act = deepq.learn(
        env,
        network=models.mlp(num_layers=1, num_hidden=20),
        total_timesteps=0,
        load_path='models/scaling_model.pkl'
    )

    # play sine curve
    env.change_rate = 1
    env.scaling_env_options['input'] = INPUTS['SINE_CURVE']

    play(act, env, 1e6)

    env.close()


if __name__ == '__main__':
    main()
