# Copyright 2019 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import collections
import random
import sys

import gym
import math
import numpy
from gym import spaces
from overrides import overrides

from .helpers import Instance, inverse_odds

INSTANCE_COSTS_PER_HOUR = {
    'c3.large': 0.192,
}
SCALING_STEP_SIZE_IN_SECONDS = 300  # Minimum resolution in AWS CloudWatch is 5 minutes

INPUTS = {
    'PRODUCTION_DATA': {
        'function': lambda: None,
        'options': {
            'path': 'data/worker_one.xlsx',
            'sheet': 'Input',
            'column': 'MessagesReceived'
        }
    },
    'SINE_CURVE': {
        'function': lambda step, max_influx, offset: math.ceil((numpy.sin(float(step) * .01) + 1) * max_influx / 2),
        'options': {
        },
    },
    'RANDOM': {
        'function': lambda step, max_influx, offset: random.randint(offset, max_influx),
        'options': {
        },
    }
}


class ScalingEnv(gym.Env):
    DEFAULTS = {
        'max_instances': 100.0,
        'min_instances': 2.0,
        'capacity_per_instance': 87,
        'cost_per_instance_per_hour': INSTANCE_COSTS_PER_HOUR['c3.large'],
        'step_size_in_seconds': SCALING_STEP_SIZE_IN_SECONDS,
        'discrete_actions': (-1, 0, 1),
        'input': INPUTS['RANDOM'],
        'offset': 500,
        'size': (300, 250),
        'change_rate': 10000
    }

    @overrides
    def __init__(self, *args, **kwargs):
        self.sim_size = (300, 250)
        # Set options and defaults
        self.scaling_env_options = {
            **self.DEFAULTS,
            **(kwargs.pop('scaling_env_options', {})),
        }
        self.actions = self.scaling_env_options['discrete_actions']
        self.num_actions = len(self.actions)
        self.action_space = spaces.Discrete(self.num_actions)
        self.observation_size = 5
        self.observation_space = spaces.Box(low=0.0, high=sys.float_info.max, shape=(1, 5))
        self.window = None

        self.max_instances = self.scaling_env_options['max_instances']
        self.min_instances = self.scaling_env_options['min_instances']
        self.capacity_per_instance = self.scaling_env_options["capacity_per_instance"]

        self.offset = self.scaling_env_options['offset']
        self.sim_size = self.scaling_env_options['size']
        self.change_rate = self.scaling_env_options['change_rate']
        self.influx_range = ((self.max_instances / 2) * self.capacity_per_instance) - self.offset
        self.max_influx = self.offset + self.influx_range
        self.max_history = math.ceil(self.sim_size[0])

        super().__init__(*args, **kwargs)

        self.reset()

    @overrides
    def step(self, action):
        self.step_idx += 1
        if self.step_idx % self.change_rate == 0:
            self.influx = self.__next_influx()

        self.hi_influx.append(self.influx)
        self.hi_instances.append(len(self.instances))
        total_items = self.influx + self.queue_size

        self.total_capacity = len(self.instances) * self.capacity_per_instance
        processed_items = min(total_items, self.total_capacity)

        self.hi_load.append(self.load)
        self.load = math.ceil(float(processed_items) / float(self.total_capacity) * 100)

        self.hi_queue_size.append(self.queue_size)
        self.queue_size = total_items - processed_items

        for instance in self.instances:
            self.total_cost += instance.curr_cost(self.step_idx)

        self.__do_action(action)
        observation = self.__get_observation()
        reward = self.__get_reward()

        done = self.queue_size > self.max_influx * 10

        return observation, reward, done, {}

    @overrides
    def reset(self):
        self.last_actions = []
        self.instances = []
        for _ in range(int(self.scaling_env_options['max_instances'] / 2)):
            self.instances.append(
                Instance(
                    step=0,
                    cost_per_hour=self.capacity_per_instance
                )
            )
        self.hi_instances = collections.deque(maxlen=self.max_history)
        self.scaling_actions = collections.deque(maxlen=self.max_history)
        self.scaling_actions.appendleft(0)
        self.total_capacity = len(self.instances) * self.capacity_per_instance
        self.load = 0.0
        self.influx_derivative = 0.0
        self.queue_size = 0.0
        self.error = 0.0
        self.step_idx = 0
        self.hi_queue_size = collections.deque(maxlen=self.max_history)
        self.hi_influx = collections.deque(maxlen=self.max_history)
        self.hi_load = collections.deque(maxlen=self.max_history)
        self.influx = self.__next_influx()
        self.reward = 0.0
        self.total_cost = 0.0
        self.collected_rewards = collections.deque(maxlen=self.max_history * 10)

        return self.__get_observation()

    @overrides
    def render(self, mode='human'):
        if len(self.collected_rewards) == 0:
            # skip rendering without at least one step
            return

        from gym_scaling.envs.rendering import PygletWindow

        stats = self.get_stats()
        if self.window is None:
            self.window = PygletWindow(self.sim_size[0] + 20, self.sim_size[1] + 20 + 20 * len(stats))

        self.window.reset()

        x_offset = 10
        sim_height = self.sim_size[1]

        self.window.rectangle(x_offset, 10, self.sim_size[0], sim_height)

        max_influx_axis = max(max(self.hi_influx), max(self.hi_queue_size))
        max_instance_axis = max(self.hi_instances)

        self.window.text(str(max_influx_axis), 1, 1, font_size=5)
        self.window.text(str(max_instance_axis), self.sim_size[0] + 5, 1, font_size=5)

        influx_scale_factor = float(sim_height) / float(max_influx_axis)
        instance_scale_factor = float(sim_height) / float(max_instance_axis)

        self.draw_data(influx_scale_factor, instance_scale_factor, x_offset)

        stats_offset = sim_height + 15
        for txt in stats:
            self.window.text(txt, x_offset, stats_offset, font_size=8)
            stats_offset += 20

        self.window.update()

    def draw_data(self, influx_scale_factor, instance_scale_factor, x_offset):
        from gym_scaling.envs.rendering import RED, BLACK, GREEN

        prev_queue_size = 0
        prev_influx = 0
        prev_instances = 0
        y_offset = self.sim_size[1] + 5
        for influx, instances, queue_size in zip(self.hi_influx, self.hi_instances, self.hi_queue_size):
            x_offset += 1

            qs_lp = (x_offset - 1, (y_offset - 2) - math.ceil(influx_scale_factor * float(prev_queue_size)))
            qs_rp = (x_offset, (y_offset - 2) - math.ceil(influx_scale_factor * float(queue_size)))
            self.window.line(qs_lp, qs_rp, color=RED)

            i_lp = (x_offset - 1, (y_offset - 1) - math.ceil(influx_scale_factor * float(prev_influx)))
            i_rp = (x_offset, (y_offset - 1) - math.ceil(influx_scale_factor * float(influx)))
            self.window.line(i_lp, i_rp, color=BLACK)

            s_lp = (x_offset - 1, (y_offset - 1) - instance_scale_factor * prev_instances)
            s_rp = (x_offset, (y_offset - 1) - instance_scale_factor * instances)
            self.window.line(s_lp, s_rp, color=GREEN)

            prev_queue_size = queue_size
            prev_influx = influx
            prev_instances = instances

    def get_stats(self):
        actions = "a: " + ' '.join(str(a) for a in self.scaling_actions)
        return [
            "frame             = %d" % self.step_idx,
            "avg reward        = %.5f" % (sum(self.collected_rewards) / len(self.collected_rewards)),
            "instance cost     = %d $" % math.ceil(self.total_cost),
            "load              = %d" % self.load,
            "instances         = %d" % len(self.instances),
            "influx            = %d" % self.influx,
            "influx_derivative = %.2f" % self.influx_derivative,
            "actions q         = %s" % actions,
            "avg queue size    = %.3f" % (sum(self.hi_queue_size, ) / len(self.hi_queue_size)),
            "avg instances     = %.3f" % (sum(self.hi_instances) / len(self.hi_instances)),
            "avg load          = %.3f" % (sum(self.hi_load) / len(self.hi_load)),
        ]

    @overrides
    def close(self):
        if self.window:
            self.window.close()
            self.window = None

    def __next_influx(self):
        return self.scaling_env_options['input']['function'](self.step_idx, self.max_influx, self.offset)

    def __do_action(self, action):
        assert 0 <= action < self.num_actions

        # add action delay of one frame, equates instance boot time of 5 minutes
        if len(self.scaling_actions) == 0:
            self.scaling_actions.append(0)

        new_action = self.actions[action]

        action = self.scaling_actions.pop()
        self.scaling_actions = [new_action]

        self.last_actions.append(new_action)

        if len(self.last_actions) > 11:
            # drop oldest (left-most) element
            self.last_actions.reverse()
            self.last_actions.pop()
            self.last_actions.reverse()

        self.reward = 0.0
        new_instances = len(self.instances) + action
        if self.max_instances >= new_instances >= self.min_instances:
            if action > 0:
                for _ in range(action):
                    self.instances.append(
                        Instance(
                            step=self.step_idx,
                            cost_per_hour=self.scaling_env_options['cost_per_instance_per_hour']
                        )
                    )
            if action < 0:
                for _ in range(-1 * action):
                    self.instances.pop(0)
        else:
            self.reward += -0.1

    def __get_observation(self):
        observation = numpy.zeros(self.observation_size)
        observation[0] = len(self.instances) / self.max_instances
        observation[1] = self.load / 100
        observation[2] = self.total_capacity
        observation[3] = self.influx
        observation[4] = self.queue_size
        return observation

    def __get_reward(self):
        normalized_load = self.load / 100
        num_instances_normalized = len(self.instances) / self.max_instances
        total_reward = (-1 * (1 - normalized_load)) * num_instances_normalized
        total_reward += self.reward
        total_reward -= inverse_odds(self.queue_size)
        self.collected_rewards.append(total_reward)
        return total_reward
