from time import perf_counter

# Read input from file
file = open("./input.txt", "r")

start_time = perf_counter()

# Let's store all coordinates, and keep track of 'walls', and let's
# sort horizontal walls by their y value, and vertical walls by their x value
horizontal_walls: list[tuple[int, tuple[int, int]]] = [] # (y, (x1, x2))
vertical_walls: list[tuple[int, tuple[int, int]]] = []   # (x, (y1, y2))
coordinates: list[tuple[int, int]] = []

def add_wall_between_points(
        prev_x: int, prev_y: int, curr_x: int, curr_y: int,
        horizontal_walls: list[tuple[int, tuple[int, int]]], 
        vertical_walls: list[tuple[int, tuple[int, int]]]
    ) -> None:
    """Add a wall between two points to the appropriate wall list."""
    if prev_x == curr_x:
        # Vertical wall
        y1, y2 = min(prev_y, curr_y), max(prev_y, curr_y)
        vertical_walls.append((curr_x, (y1, y2)))
    elif prev_y == curr_y:
        # Horizontal wall
        x1, x2 = min(prev_x, curr_x), max(prev_x, curr_x)
        horizontal_walls.append((curr_y, (x1, x2)))
    else:
        raise ValueError("This shouldn't happen: non-axis-aligned wall detected")

first_x, first_y = map(int, file.readline().rstrip().split(','))
coordinates.append((first_x, first_y))

latest_x: int = first_x
latest_y: int = first_y
for line in file:
    line = line.rstrip()
    parts = line.split(',')
    x, y = int(parts[0]), int(parts[1])
    coord = (x, y)

    add_wall_between_points(latest_x, latest_y, x, y, horizontal_walls, vertical_walls)
    coordinates.append(coord)
    latest_x, latest_y = x, y

# Need to connect last to first
add_wall_between_points(latest_x, latest_y, first_x, first_y, horizontal_walls, vertical_walls)

# Sort walls for easier processing later
horizontal_walls.sort()
vertical_walls.sort()

def find_first_greater_than(walls: list[tuple[int, tuple[int, int]]], key_value: int) -> int:
    """Binary search: find first index where wall's key (first element) > key_value."""
    left, right = 0, len(walls)
    while left < right:
        mid = (left + right) // 2
        if walls[mid][0] <= key_value:
            left = mid + 1
        else:
            right = mid
    return left

def find_first_greater_or_equal(walls: list[tuple[int, tuple[int, int]]], key_value: int) -> int:
    """Binary search: find first index where wall's key (first element) >= key_value."""
    left, right = 0, len(walls)
    while left < right:
        mid = (left + right) // 2
        if walls[mid][0] < key_value:
            left = mid + 1
        else:
            right = mid
    return left

def check_walls_crossed(walls: list[tuple[int, tuple[int, int]]], primary_min: int, primary_max: int,
                        secondary_min: int, secondary_max: int) -> bool:
    """
    Check if a rectangle crosses walls improperly.

    For horizontal walls: primary is y, secondary is x
    For vertical walls: primary is x, secondary is y

    Returns True if rectangle is valid (no improper crossings), False otherwise.
    """
    crosses: list[int] = []  # Primary values of crossed walls

    # Use binary search to find range of walls between primary_min and primary_max
    start_idx = find_first_greater_than(walls, primary_min)
    end_idx = find_first_greater_or_equal(walls, primary_max)

    # Only iterate through walls in the relevant range
    for wall_primary, (wall_sec1, wall_sec2) in walls[start_idx:end_idx]:
        # Check if wall crosses between secondary bounds
        if not (wall_sec2 <= secondary_min or wall_sec1 >= secondary_max):
            crosses.append(wall_primary)

    # Odd number of crosses means we can't be fully inside
    if len(crosses) % 2 == 1:
        return False

    # Even number of walls - check if any are separated by more than 1
    # (meaning there's a wall crossing in between)
    if len(crosses) > 0:
        for i in range(len(crosses) - 1):
            if crosses[i + 1] - crosses[i] > 1:
                return False

    return True

# Now trivially, we can just find all the areas between each pair of coordinates
# and keep track of the largest
# We now need to make sure that all values within the rectangle are also 'inside'
# the walls. We'll do this by 'counting' any walls that are inside the rectangle,
# and if we find any odd number of walls crossed, we know the rectangle is invalid.
# (as an odd number of walls suggests an area outside the polygon)
max_area = 0
best_x1, best_x2, best_y1, best_y2 = 0, 0, 0, 0
for coord1_x, coord1_y in coordinates:
    for coord2_x, coord2_y in coordinates:

        # We need to check (for coordinates of corners) if we cross ANY walls between
        # two adjacent corners. We need to take care that two walls that are adjacent are effectively
        # NO walls crossed // this is obviously now just handled in the check_walls_crossed function.
        x1, x2 = min(coord1_x, coord2_x), max(coord1_x, coord2_x)
        y1, y2 = min(coord1_y, coord2_y), max(coord1_y, coord2_y)

        # Check if horizontal walls are crossed improperly
        if not check_walls_crossed(horizontal_walls, y1, y2, x1, x2):
            continue

        # Check if vertical walls are crossed improperly
        if not check_walls_crossed(vertical_walls, x1, x2, y1, y2):
            continue

        # Calculate area
        area = (x2 - x1 + 1) * (y2 - y1 + 1) # Need +1 to account for "inclusive" area
        if area > max_area:
            best_x1, best_x2, best_y1, best_y2 = x1, x2, y1, y2
            max_area = area

end_time = perf_counter()
print(f"Execution time: {end_time - start_time:.6f} seconds")

# Finally, output the largest area found
print(f"Largest area found: {max_area}")
print(f"Coordinates of largest area: ({best_x1}, {best_y1}) to ({best_x2}, {best_y2})")