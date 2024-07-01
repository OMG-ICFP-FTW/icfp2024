#!/usr/bin/env python
# %% 
'''
In 2020, most of us have learned how to operate a spaceship. In this course we'll play a small chess-like game featuring the spaceship! The game operates on an infinite 2D chess board, with the spaceship initially located on `(0,0)`. The spaceship has a velocity `vx` and `vy`, which are initially both set to `0`. In each turn the player can increase/decrease each of those numbers by at most one, and then the piece moves `vx` steps to the right and `vy` steps up.

Moves are represented with a single digit, inspired by the old numeric pad on a computer keyboard that we used to have in the old days on Earth. For example, `7` means decreasing `vx` and increasing `vy` by `1`, while `6` means increasing `vx` by `1` and keeping `vy` the same. A path can then be represented by a sequence of digits, e.g. the path `236659` visits, in this order, the following squares: `(0,0) (0,-1) (1,-3) (3,-5) (6,-7) (9,-9) (13,-10)`.
'''

import argparse
import os
import random

from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Level:
    points: list
    pos: tuple = (0, 0)
    vel: tuple = (0, 0)
    solution: list = field(default_factory=list)

    @classmethod
    def load(cls, point_file, order_file):
        points = list()
        with open(point_file) as f:
            for line in f.read().strip().splitlines():
                x, y = map(int, line.strip().split())
                points.append((x, y))

        with open(order_file) as f:
            points = list(points[i] for i in map(int, f.read().strip().split(',')))
        return cls(points)

    @property
    def next(self):
        return self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]

    def move(self, move: int):
        assert 0 < move < 10, f"Invalid move {move}"
        vx, vy = self.vel
        if move == 1:
            vx -= 1
            vy -= 1
        elif move == 2:
            vy -= 1
        elif move == 3:
            vx += 1
            vy -= 1
        elif move == 4:
            vx -= 1
        elif move == 5:
            pass
        elif move == 6:
            vx += 1
        elif move == 7:
            vx -= 1
            vy += 1
        elif move == 8:
            vy += 1
        elif move == 9:
            vx += 1
            vy += 1
        else:
            raise ValueError(f"Invalid move {move}")
        self.vel = (vx, vy)
        self.pos = (self.pos[0] + vx, self.pos[1] + vy)
        self.solution.append(move)

    def nav(self, dst, max_tries=100000):
        """ Navigate to a given point, arriving at low velocity """
        for _ in range(max_tries):
            if self.pos == dst:
                return
            if self.next[0] < dst[0]:
                if self.next[1] < dst[1]:
                    self.move(9)
                elif self.next[1] > dst[1]:
                    self.move(3)
                else:
                    self.move(6)
            elif self.next[0] > dst[0]:
                if self.next[1] < dst[1]:
                    self.move(7)
                elif self.next[1] > dst[1]:
                    self.move(1)
                else:
                    self.move(4)
            else:
                if self.next[1] < dst[1]:
                    self.move(8)
                elif self.next[1] > dst[1]:
                    self.move(2)
                else:
                    self.move(5)
        raise ValueError("Could not navigate to destination")

    def route(self):
        for p in self.points:
            self.nav(p)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Submit 3d solution from file')
    parser.add_argument('-l','--level', help='Source file with grid', required=True)
    parser.add_argument('-v','--visit', help='Pre-generated visit order file')
    args = parser.parse_args()

    level = Level.load(args.level, args.visit)
    level.route()
    print("".join(map(str, level.solution)))
