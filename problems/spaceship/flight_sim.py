import argparse
import os
from typing import List, Tuple
import numpy as np


def read_level(level_file):
    with open(level_file) as f:
        grid = np.array([np.array(list(map(int, row.split()))) for row in f.read().strip().splitlines()])
    return grid

def read_solution(solution_file):
    with open(solution_file) as f:
        return list(map(int, list(f.read().strip())))

def calculate_path(moves) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    dv = {
        1: np.array([-1, -1]),
        2: np.array([0, -1]),
        3: np.array([1, -1]),
        4: np.array([-1, 0]),
        5: np.array([0, 0]),
        6: np.array([1, 0]),
        7: np.array([-1, 1]),
        8: np.array([0, 1]),
        9: np.array([1, 1])
    }

    positions = [np.array([0, 0])]
    velocities = [np.array([0, 0])]
    velocity = np.array([0, 0])
    for move in moves:
        velocity += dv[move]
        position = positions[-1]
        positions.append(position + velocity)
        velocities.append(np.copy(velocity))

    return np.array(positions), np.array(velocities)
        

def map_size(extents) -> Tuple[int, int]:
    return (extents[1] - extents[0]) + 1

def make_map(grid, extents):
    size = map_size(extents)
    base_map = np.zeros(size)
    for pos in grid:
        map_pos = pos - extents[0]
        base_map[map_pos[0], map_pos[1]] = 1
    return base_map
    

def display_array(display_map):
    display_map = np.flip(display_map.T, axis=0)
    for row in display_map:
        print(row.tobytes().decode('utf-8'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("level", help="file name for level")
    parser.add_argument("solution", help="file name for solution")
    args = parser.parse_args()
    level = args.level
    solution = args.solution

    print(f"Reading level from {level}")
    grid = read_level(level)
    level_max = np.max(grid, axis=0)
    level_min = np.min(grid, axis=0)
    

    print(f"Reading solution from {solution}")
    moves = read_solution(solution)
    positions, velocities = calculate_path(moves)
    pos_max = np.max(positions, axis=0)
    pos_min = np.min(positions, axis=0)

    # Calculate extents
    map_min = np.min(np.stack([level_min, pos_min], axis=0), axis=0)
    map_max = np.max(np.stack([level_max, pos_max], axis=0), axis=0)
    extents = [map_min, map_max]

    # Create base map
    base_map = make_map(grid, extents)
    base_map = np.where(base_map == 0, ".", "*")

    size = map_size(extents)
    print("Starting Position [Press Enter to step through]")
    display_map = np.copy(base_map)
    map_pos = np.array([0, 0]) - extents[0]
    last_position = np.copy(map_pos)
    display_map[map_pos[0], map_pos[1]] = "X"
    display_array(display_map)
    input()

    for step, (position, move, velocity) in enumerate(zip(positions[1:], moves, velocities[1:])):
        pos_map = np.zeros(size, dtype=np.bool)
        map_pos = position - extents[0]
        pos_map[map_pos[0], map_pos[1]] = 1
        pos_map[min(last_position[0], map_pos[0]):max(last_position[0], map_pos[0])+1, last_position[1]] = 1
        pos_map[map_pos[0], min(map_pos[1], last_position[1]):max(map_pos[1], last_position[1])+1] = 1
        last_position = np.copy(map_pos)

        pos_display = np.where(pos_map == 0, ".", "o")
        pos_display[map_pos[0], map_pos[1]] = "X"

        display_map = np.copy(base_map)
        display_map[pos_map] = pos_display[pos_map]
        
        print(f"({step}) Move: {move} -> {position}, Velocity: {velocity}")
        display_array(display_map)
        input()
    print("Done")