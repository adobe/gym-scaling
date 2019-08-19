# Copyright 2019 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

class Instance:
    def __init__(self, step, cost_per_hour):
        self.step = step
        self.cost_per_hour = cost_per_hour

    # we assume 5 minutes per step because this is the CloudWatch resolution
    def curr_cost(self, curr_step):
        steps = curr_step - self.step
        if (curr_step - self.step) % 12 == 0:
            return self.cost_per_hour / 12.0 * steps
        return 0.0


def inverse_odds(p):
    return p / (1 + p)
