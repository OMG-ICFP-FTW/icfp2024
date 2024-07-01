#!/usr/bin/env python
# %% 
'''
In 2020, most of us have learned how to operate a spaceship. In this course we'll play a small chess-like game featuring the spaceship! The game operates on an infinite 2D chess board, with the spaceship initially located on `(0,0)`. The spaceship has a velocity `vx` and `vy`, which are initially both set to `0`. In each turn the player can increase/decrease each of those numbers by at most one, and then the piece moves `vx` steps to the right and `vy` steps up.

Moves are represented with a single digit, inspired by the old numeric pad on a computer keyboard that we used to have in the old days on Earth. For example, `7` means decreasing `vx` and increasing `vy` by `1`, while `6` means increasing `vx` by `1` and keeping `vy` the same. A path can then be represented by a sequence of digits, e.g. the path `236659` visits, in this order, the following squares: `(0,0) (0,-1) (1,-3) (3,-5) (6,-7) (9,-9) (13,-10)`.
'''

import argparse
import os
import time
import random

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class Level:
    points: list
    pos: tuple = (0, 0)
    vel: tuple = (0, 0)
    solution: list = field(default_factory=list)
    max_speed: int = 300
    top_speed: int = 0
    visited: set = field(default_factory=set)

    @property
    def remaining(self):
        for p in self.points:
            if p not in self.visited:
                yield p

    @property
    def score(self):
        return len(self.visited)

    @property
    def done(self):
        return all(p in self.visited for p in self.points)

    @classmethod
    def from_index(cls, i):
        return cls.load(f"level{i}.txt")

    @classmethod
    def load(cls, point_file, order_file=None):
        points = list()
        with open(point_file) as f:
            for line in f.read().strip().splitlines():
                x, y = map(int, line.strip().split())
                points.append((x, y))
        if order_file is not None:
            with open(order_file) as f:
                points = list(points[i] for i in map(int, f.read().strip().split(',')))
        return cls(points)

    @property
    def next(self):
        return self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]

    def move(self, move: int):
        if len(self.solution) > 10_000_000:
            raise ValueError(f"Too many moves top_speed={self.top_speed}")
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
        self.top_speed = max(self.top_speed, abs(vx), abs(vy))
        self.vel = (vx, vy)
        self.pos = (self.pos[0] + vx, self.pos[1] + vy)
        self.visited.add(self.pos)
        self.solution.append(move)

    def nav(self, dst, max_tries=100000):
        """ Navigate to a given point, arriving at low velocity """
        for _ in range(max_tries):
            if self.pos == dst:
                return
            move = None
            if self.next[0] < dst[0] and self.vel[0] < self.max_speed:
                if self.next[1] < dst[1] and self.vel[1] < self.max_speed:
                    move = 9
                elif self.next[1] > dst[1] and self.vel[1] > -self.max_speed:
                    move = 3
                else:
                    move = 6
            elif self.next[0] > dst[0] and self.vel[0] > -self.max_speed:
                if self.next[1] < dst[1] and self.vel[1] < self.max_speed:
                    move = 7
                elif self.next[1] > dst[1] and self.vel[1] > -self.max_speed:
                    move = 1
                else:
                    move = 4
            else:
                if self.next[1] < dst[1] and self.vel[1] < self.max_speed:
                    move = 8
                elif self.next[1] > dst[1] and self.vel[1] > -self.max_speed:
                    move = 2
                else:
                    move = 5
            assert move is not None, f"Could not navigate to {dst} from {self.pos}"
            self.move(move)
        raise ValueError("Could not navigate to destination")

    def next_point(self, choices=3):
        remaining = list(self.remaining)
        # sort by distance to self.next
        remaining.sort(key=lambda p: abs(p[0] - self.next[0]) + abs(p[1] - self.next[1]))
        # pick the closest for now
        return random.choice(remaining[:choices])

    def route(self, timeout=10, current_best=None, choices=3):
        start = time.time()
        while not self.done:
            p = self.next_point(choices)
            self.nav(p)
            if time.time() > start + timeout:
                print("Timeout")
                exit(1)
            if current_best is not None:
                if self.score > current_best:
                    print(f"Current score {self.score} is worse than best {current_best}")
                    exit(1)


def main(filename, visit=None, output=None, max_speed=50, timeout=10, current_best=None, choices=3):
    level = Level.load(filename, visit)
    level.max_speed = max_speed
    level.route(timeout=timeout, current_best=current_best, choices=choices)
    print("Top speed:", level.top_speed, "max speed:", level.max_speed, "solution length:", len(level.solution))

    if output:
        # check existing solution
        if os.path.exists(output):
            # Get existing score
            with open(output) as f:
                score = len(f.read().strip())
            if len(level.solution) >= score:
                print(f"Existing solution is better: {score} <= {len(level.solution)}")
                return
        # Save new solution
        with open(output, 'w') as f:
            f.write("".join(map(str, level.solution)))
            print(f"Saved solution to {output}")
    else:
        print("".join(map(str, level.solution)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Submit 3d solution from file')
    parser.add_argument('-l','--level', help='Source file with grid', required=True)
    parser.add_argument('-v','--visit', default=None, help='Pre-generated visit order file')
    parser.add_argument('-o','--output', default=None, help='Output file')
    parser.add_argument('-m','--max-speed', default=50, type=int, help='Max speed')
    parser.add_argument('-t','--timeout', default=10, type=int, help='Timeout')
    parser.add_argument('-c','--choices', default=3, type=int, help='Number of choices to consider')
    args = parser.parse_args()
    if os.path.exists(args.output):
        with open(args.output) as f:
            score = len(f.read().strip())
    else:
        score = None
    main(args.level, args.visit, args.output, args.max_speed, args.timeout, current_best=score, choices=args.choices)