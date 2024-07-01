import heapq
from pathlib import Path


move_map = {
    "1": (-1, -1),
    "2": (0, -1),
    "3": (1, -1),
    "4": (-1, 0),
    "5": (0, 0),
    "6": (1, 0),
    "7": (-1, 1),
    "8": (0, 1),
    "9": (1, 1),
}


def apply_move(vx, vy, move):
    dx, dy = move_map[move]
    new_vx = vx + dx
    new_vy = vy + dy
    return new_vx, new_vy


def move_spaceship(x, y, vx, vy):
    new_x = x + vx
    new_y = y + vy
    return new_x, new_y


def heuristic(x, y, target_squares):
    return min(abs(x - tx) + abs(y - ty) for tx, ty in target_squares)


def find_path(target_squares):
    target_set = set(target_squares)
    pq = []
    heapq.heappush(pq, (0, 0, 0, 0, 0, 0, ""))  # (priority, steps, x, y, vx, vy, path)
    visited = set((0, 0, 0, 0))

    while pq:
        _, steps, x, y, vx, vy, path = heapq.heappop(pq)

        # Check if we've reached a target square
        if (x, y) in target_set:
            target_set.remove((x, y))
            if not target_set:
                return path
            pq = []
            visited = set((x, y, vx, vy))

        # Explore all possible moves
        for move in move_map.keys():
            new_vx, new_vy = apply_move(vx, vy, move)
            new_x, new_y = move_spaceship(x, y, new_vx, new_vy)
            if (new_x, new_y, new_vx, new_vy) not in visited:
                visited.add((new_x, new_y, new_vx, new_vy))
                priority = steps + 1 + heuristic(new_x, new_y, target_set)
                heapq.heappush(pq, (priority, steps + 1, new_x, new_y, new_vx, new_vy, path + move))

    return "No path found"


points = list()
with open(Path(__file__).parent / "level1.txt") as f:
    for line in f.read().strip().splitlines():
        x, y = map(int, line.strip().split())
        points.append((x, y))
path = find_path(points)
print("Spaceship path:", path)
