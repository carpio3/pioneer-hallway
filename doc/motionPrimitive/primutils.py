"""
Author: Jordan Ramsdell
Desc: Contains functions and classes useful for dealing with primitives.
"""
from collections import namedtuple
import re
import sys
import math

ActionResult = namedtuple("ActionResult", "")
PrimitiveResult = namedtuple("PrimitiveResult",
                             "name la wa vkey wkey hkey x y h path")
PrimitiveEntry = namedtuple("PrimitiveEntry", "x y h path")

class Primitive(object):
    def __init__(self, name, va, wa, config, entries):
        self.name = name
        self.va = va
        self.wa = wa
        self.config = config
        self.entries = entries

    def get_entry(self, state_v, state_w, state_h):
        """
        :param state_v: state's linear velocity (in m/s)
        :param state_w: state's angular velocity (in radians/s)
        :param state_h: state's heading (in radians)
        :return: tuple of (x y h path)
        """
        vkey = round(state_v / self.config["linear_velocity_divisor"])
        wkey = round(state_w / self.config["angular_velocity_divisor"])
        hkey = round(state_h / self.config["heading_divisor"])
        return self.entries.get((self.name, vkey, wkey, hkey), None)


    def apply(self, x, y, state_v, state_w, state_h):
        """
        :param x: Current x-position (in map units) of robot
        :param y: Current y-position (in map units) of robot
        :param state_v: Current velocity (in m/s) of robot
        :param state_w: Current angular velocity (in radians/s) of robot
        :param state_h: Current heading (in radians) of robot
        :return: tuple (x, y, heading)
        """
        ad = self.config["action_duration"]
        v = state_v * ad + self.va * 0.5
        w = state_w * ad + self.wa * 0.5
        dx = x + (v * math.cos(w)) / 0.05
        dy = y + (v * math.sin(w)) / 0.05
        h = state_h + w

        return dx, dy, h




def read_primitives(filename):
    primitive_controls = set()
    primitive_entries = {}

    with open(filename) as f:
        lines = f.readlines()

    config = {
       "action_duration":float(lines[0]),
        "linear_velocity_divisor":float(lines[1]),
        "angular_velocity_divisor":float(lines[2]),
        "heading_divisor":float(lines[3]),
    }

    for line in lines[4:]:
        elements = line.split("\t")
        if len(elements) < 10:
            continue

        p = PrimitiveResult(*(line.split("\t")))
        primitive_controls.add((p.name, float(p.la), float(p.wa)))
        path = [(int(i.group(1)), int(i.group(2)))
                for i in re.finditer("([\-0-9]+), ([\-0-9]+)", p.path)]

        pentry = PrimitiveEntry(float(p.x), float(p.y), float(p.h), path)
        primitive_entries[(p.name, int(p.vkey), int(p.wkey), int(p.hkey))] = pentry

    primitives = [Primitive(i[0], i[1], i[2], config, primitive_entries) for
                  i in primitive_controls]

    return primitives

'''
add by Tianyi Mar / 8 / 2017
'''
def read_primitives_with_duration(filename):
    primitive_controls = set()
    primitive_entries = {}

    with open(filename) as f:
        lines = f.readlines()

    config = {
       "action_duration":float(lines[0]),
        "linear_velocity_divisor":float(lines[1]),
        "angular_velocity_divisor":float(lines[2]),
        "heading_divisor":float(lines[3]),
    }

    for line in lines[4:]:
        elements = line.split("\t")
        if len(elements) < 10:
            continue

        p = PrimitiveResult(*(line.split("\t")))
        primitive_controls.add((p.name, float(p.la), float(p.wa)))
        path = [(int(i.group(1)), int(i.group(2)))
                for i in re.finditer("([\-0-9]+), ([\-0-9]+)", p.path)]

        pentry = PrimitiveEntry(float(p.x), float(p.y), float(p.h), path)
        primitive_entries[(p.name, int(p.vkey), int(p.wkey), int(p.hkey))] = pentry

    primitives = [Primitive(i[0], i[1], i[2], config, primitive_entries) for
                  i in primitive_controls]

    return (primitives, float(lines[0]))



# if __name__ == '__main__':
#     primitives = read_primitives(sys.argv[1])
#     print(primitives[0].get_entry(0.5, math.pi/5, 1.2 * math.pi))
#     print(primitives[0].apply(2, 2, 0.2, math.pi/8, math.pi/8))




