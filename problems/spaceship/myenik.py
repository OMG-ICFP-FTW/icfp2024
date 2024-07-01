import argparse
import random
import os
from typing import List, Tuple
from dataclasses import dataclass, field
import numpy as np
from concorde.tsp import TSPSolver

# XXX TODO GARBAGE ALERT! TODO XXX
#
# This only runs locally after installing pyconcorde since bazel python stuff
# pukes trying to install it lol


class Level:
    @property
    def solved(self):
        return len(self.remaining) == 0

    @property
    def score(self):
        return len(self.solution) if self.solved else None

    @property
    def nex(self):
        return self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]

    def __init__(self, level_file):
        points = []
        xs = []
        ys = []
        with open(level_file) as file:
            for line in file.read().strip().splitlines():
                x, y = map(int, line.strip().split())
                points.append((x, y))
                xs.append(x)
                ys.append(y)
        self.point_array = np.array(points)
        self.xs = np.array(xs)
        self.ys = np.array(ys)
        print('lmao', self.point_array.shape)
        print('lmao', self.xs.shape)
        print('lmao', self.ys.shape)

    def route(self):
        solver = TSPSolver.from_data(
        self.xs,
        self.ys,
        norm="EUC_2D"
        )

        tour_data = solver.solve(time_bound = 10.0, verbose = True, random_seed = 42) # solve() doesn't seem to respect time_bound for certain values?
        print('ayyyyyyyy', tour_data)
        print('ayyyyyyyy', tour_data.found_tour)
        return tour_data

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

    def save(self, path):
        """ Save level solution if better """
        assert self.solved and self.score > 0, "Cannot save unsolved level"
        if os.path.exists(path):
            with open(path) as f:
                prev_score = len(f.read().strip())
            if self.score >= prev_score:
                return
        solution = ''.join(map(str, self.solution))
        with open(path, 'w') as f:
            f.write(solution)
        print(f"Saved solution {self.i}, score", self.score)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Submit 3d solution from file')
    parser.add_argument('-f','--file', help='Source file with grid', required=True)
    parser.add_argument('-v','--visit', help='Pre-generated visit order file')
    parser.add_argument('-o','--out', help='Output file to save solution', required=True)
    parser.add_argument('-r','--route', help='', default=False, action='store_true')
    parser.add_argument('N', type=int)
    args = parser.parse_args()

    level = Level(args.file)
    level.route()
    #level.solve().save(args.out)

