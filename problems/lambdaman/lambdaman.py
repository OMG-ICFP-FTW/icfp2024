#!/usr/bin/env python
# %% lambdaman solver
import os
import random
import time
from dataclasses import dataclass


@dataclass
class Level:
    i: int
    grid: list  # list of lists
    solution: str = ''

    @classmethod
    def load(cls, i: int):
        with open(f"./level{i}.txt") as f:
            grid = [list(row) for row in f.read().strip().splitlines()]
        return cls(i, grid)

    def __str__(self):
        return self.solution + "\n" + "\n".join("".join(row) for row in self.grid)

    @property
    def height(self):
        return len(self.grid)
    
    @property
    def width(self):
        return len(self.grid[0])

    @property
    def remaining(self):
        """ number of remaining pills """
        return sum(row.count('.') for row in self.grid)
    
    @property
    def solved(self):
        return self.remaining == 0
    
    @property
    def score(self):
        return len(self.solution) if self.solved else None
    
    @property
    def L(self):
        """ location of Lambda in the grid """
        for i, row in enumerate(self.grid):
            if 'L' in row:
                return (i, row.index('L'))
        raise ValueError("No Lambda in the grid")

    def direction(self, src, dst):
        """ Get the direction from src to dst """
        assert src != dst, f"Invalid direction: {src} -> {dst}"
        x1, y1 = src
        x2, y2 = dst
        if x1 < x2:
            assert y1 == y2, f"Invalid direction: {src} -> {dst}"
            return 'D'
        elif x1 > x2:
            assert y1 == y2, f"Invalid direction: {src} -> {dst}"
            return 'U'
        elif y1 < y2:
            assert x1 == x2, f"Invalid direction: {src} -> {dst}"
            return 'R'
        elif y1 > y2:
            assert x1 == x2, f"Invalid direction: {src} -> {dst}"
            return 'L'
        else:
            raise ValueError(f"Invalid direction: {src} -> {dst}")

    def dist(self, src, dst):
        """ Manhattan distance """
        return abs(src[0] - dst[0]) + abs(src[1] - dst[1])

    def neighbors(self, x, y):
        """ Neighbors of a location """
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.height and 0 <= ny < self.width and self.grid[nx][ny] != '#':
                yield (nx, ny)

    def pills(self):
        """ Remaining pill locations, sorted by distance to Lambda """
        locations = []
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell == '.':
                    locations.append((i, j))
        return locations

    def closest(self):
        """ Get (a) closest pill """
        L = self.L
        pills = self.pills()
        dist = min(self.dist(L, pill) for pill in pills)
        options = [pill for pill in pills if self.dist(L, pill) == dist]
        return random.choice(options)

    def step(self, direction):
        """ Step lambda in a direction """
        assert direction in 'URDL', f"Invalid direction: {direction}"
        x, y = self.L
        dx, dy = {'U': (-1, 0), 'R': (0, 1), 'D': (1, 0), 'L': (0, -1)}[direction]
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < self.height and 0 <= new_y < self.width and self.grid[new_x][new_y] != '#':
            self.grid[x][y] = ' '
            self.grid[new_x][new_y] = 'L'
            self.solution += direction
        else:
            raise ValueError(f"Invalid move: {direction}")
        
    def astar(self, dst):
        """ Compute shortest path from Lambda to destination """
        # Use manhattan distance as heuristic
        def h(node):
            return self.dist(node, dst)
        
        # A* search
        start = self.L
        frontier = [(h(start), start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        while frontier:
            frontier.sort()
            _, current = frontier.pop(0)
            if current == dst:
                break
            for neighbor in self.neighbors(*current):
                new_cost = cost_so_far[current] + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + h(neighbor)
                    frontier.append((priority, neighbor))
                    came_from[neighbor] = current
        # Reconstruct path
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        # Convert to directions
        for i in range(len(path) - 1):
            self.step(self.direction(path[i], path[i + 1]))
    
    def solve(self):
        """ always move to the closest pill """
        while not self.solved:
            self.astar(self.closest())
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
        with open(path, 'w') as f:
            f.write(self.solution)
        print(f"Saved solution {self.i}, score", self.score)


# %% run the levels
while True:
    for i in range(1, 22):
        if os.path.exists(f"level{i}.txt"):
            level = Level.load(i)
            level.solve().save()
