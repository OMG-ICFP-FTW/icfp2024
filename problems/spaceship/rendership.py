#!/usr/bin/env python
# %%
import os
from dataclasses import dataclass, field
from PIL import Image, ImageDraw


@dataclass
class Level:
    i: int
    stars: list
    path: list = field(default_factory=list)
    solution: str = ''
    px: int = 0
    py: int = 0
    vx: int = 0
    vy: int = 0

    def extents(self):
        # get max extents of combined stars and path
        x, y = zip(*(self.stars + self.path + [(self.px, self.py)]))
        return (min(x), min(y), max(x), max(y))

    @classmethod
    def load(cls, i):
        filename = f"level{i}.txt"
        points = []
        with open(filename) as f:
            for line in f.read().strip().splitlines():
                x, y = map(int, line.split())
                points.append((x, y))
        level = cls(i, points)
        solution = f"solution{i}.txt"
        if os.path.exists(solution):
            with open(solution) as f:
                level.walk(f.read().strip())
        return level

    def move(self, move):
        assert move in '123456789', f'Invalid move {move}'
        if move == '1':
            self.vx -= 1
            self.vy -= 1
        elif move == '2':
            self.vy -= 1
        elif move == '3':
            self.vx += 1
            self.vy -= 1
        elif move == '4':
            self.vx -= 1
        elif move == '5':
            pass
        elif move == '6':
            self.vx += 1
        elif move == '7':
            self.vx -= 1
            self.vy += 1
        elif move == '8':
            self.vy += 1
        elif move == '9':
            self.vx += 1
            self.vy += 1
        else:
            raise ValueError(f"Invalid move {move}")
        self.path.append((self.px, self.py))
        self.px += self.vx
        self.py += self.vy
        self.solution += str(move)

    def walk(self, moves):
        for move in moves:
            self.move(move)

    def render(self):
        minx, miny, maxx, maxy = self.extents()
        width = maxx - minx + 1
        height = maxy - miny + 1
        assert width < 1000 and height < 1000, f"too big {width} x {height}"
        # Create a blank image
        img = Image.new('RGB', (width, height), 'black')
        draw = ImageDraw.Draw(img)
        # Draw the stars
        stars = [(x - minx, y - miny) for x, y in self.stars]
        draw.point(stars, fill=(255, 255, 255, 255))
        # Draw the trajectory
        path = [(x - minx, y - miny) for x, y in self.path]
        draw.point(path, fill=(255, 0, 0, 100))
        # Draw the spaceship
        ship = [(self.px - minx, self.py - miny)]
        draw.point(ship, fill=(0, 0, 255, 100))
        return img

    def show(self, big=400):
        img = self.render()
        if img.width < big or img.height < big:
            scale = big // max(img.width, img.height)
            size = (img.width * scale, img.height * scale)
            display(img.resize(size))
        display(img)


level = Level.load(3)
level.show()