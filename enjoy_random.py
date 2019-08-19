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


def main():
    env = gym.make('Scaling-v0')

    for _ in range(1):
        observation = env.reset()
        for _ in range(20000):
            action = env.action_space.sample()  # random action
            observation, reward, done, info = env.step(action)
            env.render()
            if done:
                break
    env.close()


if __name__ == '__main__':
    main()
