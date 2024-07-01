#!/usr/bin/env python
# %%
import os
from dataclasses import dataclass, field


@dataclass
class Level:
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
        solution = f"solution{i}.txt"
        return cls.from_files(filename, solution)

    @classmethod
    def from_files(cls, filename, solution=None):
        points = []
        with open(filename) as f:
            for line in f.read().strip().splitlines():
                x, y = map(int, line.split())
                points.append((x, y))
        level = cls(points)
        if solution and os.path.exists(solution):
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

        # Determine the scaling factor to fit the content in a 60x60 area
        scale = 600 / max(content_width, content_height)

        def transform(x, y):
            x_scaled = (x - minx) * scale
            y_scaled = (y - miny) * scale
            return x_scaled + 200, y_scaled + 200

        svg = '<svg width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">\n'
        
        # Draw a border around the content area
        svg += '  <rect x="200" y="200" width="600" height="600" fill="white" stroke="gray" stroke-width="5" />\n'
        
        # Draw the stars
        for x, y in self.stars:
            cx, cy = transform(x, y)
            svg += f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="black" />\n'
        
        # Draw the trajectory
        if self.path:
            path_points = " ".join([f"{transform(x, y)[0]:.1f},{transform(x, y)[1]:.1f}" for x, y in self.path])
            svg += f'  <polyline points="{path_points}" fill="none" stroke="red" stroke-width="7" stroke-opacity="0.5"/>\n'
        
        # Draw the spaceship
        ship_x, ship_y = transform(self.px, self.py)
        svg += f'  <circle cx="{ship_x:.1f}" cy="{ship_y:.1f}" r="15" fill="blue" fill-opacity="0.5"/>\n'
        
        svg += '</svg>'
        return svg

    def save_svg(self, filename):
        svg = self.render_svg()
        with open(filename, 'w') as f:
            f.write(svg)
        print(f"SVG saved to {filename}")


def main(filename, solution=None):
    level = Level.from_files(filename, solution)
    level.save_svg('output.svg')


if __name__ == '__main__':
    for i in range(1,26):
        try:
            Level.load(i).save_svg(f'level{i}.svg')
        except Exception as e:
            print(f"Error processing level {i}: {e}")