#!/usr/bin/env python
# %% 
'''
In 2020, most of us have learned how to operate a spaceship. In this course we'll play a small chess-like game featuring the spaceship! The game operates on an infinite 2D chess board, with the spaceship initially located on `(0,0)`. The spaceship has a velocity `vx` and `vy`, which are initially both set to `0`. In each turn the player can increase/decrease each of those numbers by at most one, and then the piece moves `vx` steps to the right and `vy` steps up.

Moves are represented with a single digit, inspired by the old numeric pad on a computer keyboard that we used to have in the old days on Earth. For example, `7` means decreasing `vx` and increasing `vy` by `1`, while `6` means increasing `vx` by `1` and keeping `vy` the same. A path can then be represented by a sequence of digits, e.g. the path `236659` visits, in this order, the following squares: `(0,0) (0,-1) (1,-3) (3,-5) (6,-7) (9,-9) (13,-10)`.
'''

import random
import os
from typing import List, Tuple
from dataclasses import dataclass, field

@dataclass
class Level:
    i: int
    remaining: set
    pos: tuple = (0, 0)
    vel: tuple = (0, 0)
    solution: list = field(default_factory=list)

    @classmethod
    def load(cls, i):
        points = set()
        with open(f'level{i}.txt') as file:
            for line in file.read().strip().splitlines():
                x, y = map(int, line.strip().split())
                points.add((x, y))
        return cls(i, points)
    
    @property
    def solved(self):
        return len(self.remaining) == 0

    @property
    def score(self):
        return len(self.solution) if self.solved else None

    @property
    def nex(self):
        return self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]

    def move(self, move: int):
        assert move in range(1, 10), f"Invalid move {move}"
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
        if self.pos in self.remaining:
            self.remaining.remove(self.pos)
        self.solution.append(move)

    def nav(self, dst, max_tries=100000):
        """ Navigate to a given point, arriving at low velocity """
        for _ in range(max_tries):
            if self.pos == dst:
                return
            if self.nex[0] < dst[0]:
                if self.nex[1] < dst[1]:
                    self.move(9)
                elif self.nex[1] > dst[1]:
                    self.move(3)
                else:
                    self.move(6)
            elif self.nex[0] > dst[0]:
                if self.nex[1] < dst[1]:
                    self.move(7)
                elif self.nex[1] > dst[1]:
                    self.move(1)
                else:
                    self.move(4)
            else:
                if self.nex[1] < dst[1]:
                    self.move(8)
                elif self.nex[1] > dst[1]:
                    self.move(2)
                else:
                    self.move(5)
        raise ValueError("Could not navigate to destination")

    def solve(self):
        while not self.solved:
            point = random.choice(list(self.remaining))
            self.nav(point)
        print(f"Solved level {self.i} in {len(self.solution)} moves")
        return self

    def save(self):
        """ Save level solution if better """
        assert self.solved and self.score > 0, "Cannot save unsolved level"
        path = f"./solution{self.i}.txt"
        if os.path.exists(path):
            with open(path) as f:
                prev_score = len(f.read().strip())
            if self.score >= prev_score:
                return
        solution = ''.join(map(str, self.solution))
        with open(path, 'w') as f:
            f.write(solution)
        print(f"Saved solution {self.i}, score", self.score)

# %%
for _ in range(100):
    for i in range(1, 22):
        level = Level.load(i)
        try:
            level.solve().save()
        except ValueError as e:
            print("Error:", e)