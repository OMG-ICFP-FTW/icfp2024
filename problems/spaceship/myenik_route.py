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

    def route(self, path):
        solver = TSPSolver.from_data(
        self.xs,
        self.ys,
        norm="EUC_2D"
        )

        tour_data = solver.solve(time_bound = 50.0, verbose = True, random_seed = 69) # solve() doesn't seem to respect time_bound for certain values?
        print('ROUTED - ', tour_data)
        route = ','.join(map(str, tour_data.tour))
        with open(path, 'w') as f:
            f.write(route)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Submit 3d solution from file')
    parser.add_argument('-f','--file', help='Source file with grid', required=True)
    parser.add_argument('-o','--out', help='Output file to save solution', required=True)
    args = parser.parse_args()

    level = Level(args.file)
    level.route(args.out)
    #level.solve().save(args.out)


