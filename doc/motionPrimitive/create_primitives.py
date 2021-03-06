"""
Author: Jordan Ramsdell
Desc: generates primitives and prints them to standard out.
Usage: python3 create_primitives.py
"""
from math import *
import numpy as np
from itertools import *
from collections import namedtuple


map_scale             = 0.05            # scale in meters per cell in map
action_duration       = 0.25            # duration actions take (in seconds)
max_linear_velocity   = 1.2             # max linear velocity in meters per second
max_acceleration      = 0.3             # max acceleration in meters per second

# the following options are for fine-tuning the discretization of our states
lv_states             = [action_duration * i for i in
                         [0, 0.075, 0.15, 0.25, 0.3,
                          0.375, 0.45, 0.525, 0.6,
                          0.675, 0.75, 0.825, 0.9,
                          0.975, 1.05, 1.125, 1.2]]
heading_states        = [i * pi/8 for i in range(17)]

acceleration_controls = [-0.3 * action_duration, 0, 0.3 * action_duration]
av_controls           = [-2 * pi/4, -pi/4, 0, pi/4, 2 * pi/4]
av_bounds             = [-2 * pi/4, 2 * pi/4]
lv_bounds             = [0, 1.2 * action_duration]


# class ActionResult(object):
#     def __init__(self, lv, heading, ):



ActionResult = namedtuple("ActionResult", "state_v state_w state_heading x y heading collision_cells")

class Primitive(object):
    def __init__(self, name, accel, av):
        self.name = name
        self.accel = accel
        self.av = av

        self.action_results = self.get_results()

    def generate_states(self):
        for lv in lv_states:
            if lv_bounds[0] <= lv + self.accel * action_duration <= lv_bounds[1]:
                for heading in heading_states:
                    for w in av_controls:
                        if av_bounds[0] <= w + self.av <= av_bounds[1]:
                            yield (heading, lv, w)

    def get_results(self):
        action_results = []
        for state in self.generate_states():
            action_results.append(self.apply_primitive(*state))
        return action_results

    def apply_primitive(self, heading, lv, w):
        collision_cells = set()
        x, y, cur_lv, cur_av = 0, 0, 0, 0

        for t in np.arange(0, 1.000001, 0.001):
            cur_lv = lv * t + self.accel * 0.5 * t**2
            cur_av = heading + w*t + self.av * 0.5 * t**2
            x = cur_lv * cos(cur_av)
            y = cur_lv * sin(cur_av)
            collision_cells.add((int(x / map_scale), int(y / map_scale)))

        new_heading = heading + w + self.av * 0.5
        if new_heading < 0:
            new_heading = 2 * pi + new_heading
        elif new_heading > 2 * pi:
            new_heading = new_heading - 2 * pi

        return ActionResult(
                            round(lv / (0.075 * action_duration)),
                            round(w / (pi / 4)),
                            round(heading / (pi / 8)),
            # int(heading / (pi / 8)),
                            x / map_scale, y / map_scale,
                            new_heading, collision_cells)

    def __str__(self):
        out = ""
        base = [
            self.name,               # Col0: Primitive Name
            self.accel,              # Col1: Primitive Acceleration
            self.av,                 # Col2: Primitive Angular Accel
        ]
        base = [str(i) for i in base]

        for result in self.action_results:
            collisions = " ".join(map(str, result.collision_cells))
            action_out = [
                result.state_v,              # Col3: Initial Velocity Key
                result.state_w,              # Col4: Initial Ang. Velocity Key
                result.state_heading,        # Col5: Initial Heading Key
                result.x,                    # Col6: Final x Location
                result.y,                    # Col7: Final y Location
                result.heading,              # Col8: Final heading
                collisions                   # Col9: Cells to check for collision
            ]
            action_out = [str(i) for i in action_out]

            out += "\t".join(chain(base, action_out)) + "\n"

        return out



if __name__ == '__main__':
    primitives = []
    counter = 0
    # for result in p.action_results:
    #     print(result)
    for acc in acceleration_controls:
        for av in av_controls:
            primitives.append(Primitive("a{}".format(counter), acc, av))
            counter += 1


    print(0.25)                         # action duration
    print(0.075)                          # linear velocity divisor
    print(pi/4)                         # angular velocity divisor
    print(pi/8)                         # heading divisor
    for p in primitives:
        print(p)

