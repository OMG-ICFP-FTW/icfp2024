#!/usr/bin/env python
# %%
import os
from dataclasses import dataclass, field


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

    def render_svg(self):
        minx, miny, maxx, maxy = self.extents()
        content_width = maxx - minx + 1
        content_height = maxy - miny + 1

        # Calculate the new dimensions with extra space
        total_width = content_width * 3
        total_height = content_height * 3
        offset_x = content_width
        offset_y = content_height

        stroke_width = max(total_width, total_height) / 100
        star_size = stroke_width * 2
        ship_size = stroke_width * 2
        print('stroke_width', stroke_width)
        print('star_size', star_size)
        print('ship_size', ship_size)

        svg = f'<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">\n'
        
        # Draw the stars
        for x, y in self.stars:
            svg += f'  <circle cx="{x - minx + offset_x}" cy="{y - miny + offset_y}" r="{star_size}" fill="black" />\n'
        
        # Draw the trajectory
        if self.path:
            path_points = " ".join([f"{x - minx + offset_x},{y - miny + offset_y}" for x, y in self.path])
            svg += f'  <polyline points="{path_points}" fill="none" stroke="red" stroke-width="{stroke_width}" />\n'
        
        # Draw the spaceship
        svg += f'  <circle cx="{self.px - minx + offset_x}" cy="{self.py - miny + offset_y}" r="{ship_size}" fill="blue" />\n'
        
        svg += '</svg>'
        return svg

    def save_svg(self, filename):
        svg = self.render_svg()
        with open(filename, 'w') as f:
            f.write(svg)
        print(f"SVG saved to {filename}")


for i in range(30):
    try:
        print(f"level {i}")
        level = Level.load(i)
        level.save_svg(f"level{i}.svg")
    except Exception as e:
        print(e)