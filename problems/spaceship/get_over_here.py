def get_over_here(start, end):
    current_position = list(start)
    velocity = [0, 0]
    path = [list(start)]

    # Calculate distance to travel in both dimensions
    distances = [end[0] - start[0], end[1] - start[1]]
    # Calculate the ratio of the distances
    max_distance = max(abs(distances[0]), abs(distances[1]))
    ratio = [abs(distances[0] / max_distance), abs(distances[1] / max_distance)]
    print(ratio)

    # Movement multipliers to control velocity increments
    movement_multipliers = [ratio[0] / min(ratio), ratio[1] / min(ratio)]
    print(movement_multipliers)
    movement_counters = [0.0, 0.0]

    while current_position != end and len(path) < 31:
        for i in range(2):
            if current_position[i] != end[i]:
                # Increment the movement counter for this dimension
                movement_counters[i] += movement_multipliers[i]

                # Determine the direction to move in
                direction = 1 if distances[i] > 0 else -1

                # Check if it's time to increment velocity in this dimension
                if movement_counters[i] >= 1:
                    # Calculate new velocity proposal
                    new_velocity = velocity[i] + direction
                    predicted_position = current_position[i] + new_velocity

                    # Check for overshooting
                    if (direction == 1 and predicted_position > end[i]) or (
                        direction == -1 and predicted_position < end[i]
                    ):
                        velocity[i] = end[i] - current_position[i]
                    else:
                        velocity[i] = new_velocity

                    # Reset counter after velocity increment
                    movement_counters[i] -= 1

        # Update current position based on velocity
        current_position = [current_position[i] + velocity[i] for i in range(2)]
        path.append(list(current_position))
        print("Current position:", current_position)
        print("End position:", end)
        print("Velocity:", velocity)

    return path


# Example usage:
start_point = [0, 0]
end_point = [11, 6]
# start_point = [-11, 220]
# end_point = [1, 38]
path = get_over_here(start_point, end_point)
print("Path taken:", path)
