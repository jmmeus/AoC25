from time import perf_counter

# Read input from file
file = open("./input.txt", "r")

start_time_approach1 = perf_counter()

# Let's store all coordinates, and create a sorted list of indexes
# to track x and y orders
coordinates: list[tuple[int, int]] = []
for line in file:
    line = line.rstrip()
    parts = line.split(',')
    coord = (int(parts[0]), int(parts[1]))
    coordinates.append(coord)

# Now trivially, we can just find all the areas between each pair of coordinates
# and keep track of the largest
max_area_approach1 = 0
for x1, y1 in coordinates:
    for x2, y2 in coordinates:
        # Calculate area
        area = (abs(x2 - x1) + 1) * (abs(y2 - y1) + 1) # Need +1 to account for "inclusive" area
        if area > max_area_approach1:
            max_area_approach1 = area

end_time_approach1 = perf_counter()
print(f"Execution time: {end_time_approach1 - start_time_approach1:.6f} seconds")

# Finally, output the largest area found
print(f"Largest area found: {max_area_approach1}")

# I'd like to try approaching this slightly differently. If we assume a roughly uniform distribution
# of points, then the largest rectangle should be formed by points that are "far apart".
# So, having sorted lists of x and y coordinates, we can try to find the first shared index
# between the two sorted lists, and the last shared index, and then only test combinations
# of points that are before the first shared index and after the last shared index, virtually
# 'extending' out from the smallest bounding box that *likely* contains the largest rectangle.

print("\n=== NEW APPROACH ===\n")


# New approach: find first + last shared index and test all pairs before it
file.seek(0)

start_time_approach2 = perf_counter()

# Let's store all coordinates, and create a sorted list of indexes
coordinates: list[tuple[int, int]] = []
unsorted_x: list[tuple[int, int]] = []
unsorted_y: list[tuple[int, int]] = []
for line in file:
    line = line.rstrip()
    parts = line.split(',')
    coord = (int(parts[0]), int(parts[1]))
    coordinates.append(coord)
    unsorted_x.append((coord[0], len(coordinates) - 1))
    unsorted_y.append((coord[1], len(coordinates) - 1))

sorted_x = sorted(unsorted_x)
sorted_y = sorted(unsorted_y)
sorted_x_indexes = [index for _, index in sorted_x]
sorted_y_indexes = [index for _, index in sorted_y]

# Create position lookup dictionaries to avoid O(n) .index() calls
x_idx_to_pos = {idx: pos for pos, idx in enumerate(sorted_x_indexes)}
y_idx_to_pos = {idx: pos for pos, idx in enumerate(sorted_y_indexes)}

def find_shared_index(
        sorted_x_indexes: list[int], sorted_y_indexes: list[int],
        x_idx_to_pos: dict[int, int], y_idx_to_pos: dict[int, int], 
        reverse: bool = False
    ) -> tuple[int, int, int]:
    """Find a shared index between two sorted lists of indexes, optionally searching from the end."""
    searched_indexes: set[int] = set()
    shared_index = 0 if reverse else -1
    shared_pos_x = 0 if reverse else -1
    shared_pos_y = 0 if reverse else -1

    iterator = zip(sorted_x_indexes, sorted_y_indexes)
    if reverse:
        iterator = zip(reversed(sorted_x_indexes), reversed(sorted_y_indexes))

    for x_list_idx, y_list_idx in iterator:
        if x_list_idx == y_list_idx:
            shared_index = x_list_idx
            shared_pos_x = x_idx_to_pos[x_list_idx]
            shared_pos_y = y_idx_to_pos[y_list_idx]
            break
        elif x_list_idx in searched_indexes:
            shared_index = x_list_idx
            shared_pos_x = x_idx_to_pos[x_list_idx]
            shared_pos_y = y_idx_to_pos[x_list_idx]
            break
        elif y_list_idx in searched_indexes:
            shared_index = y_list_idx
            shared_pos_x = x_idx_to_pos[y_list_idx]
            shared_pos_y = y_idx_to_pos[y_list_idx]
            break
        else:
            searched_indexes.add(x_list_idx)
            searched_indexes.add(y_list_idx)

    return shared_index, shared_pos_x, shared_pos_y

# Find the first shared index between the two sorted lists
first_shared_index, first_shared_pos_x, first_shared_pos_y = find_shared_index(
    sorted_x_indexes, sorted_y_indexes, x_idx_to_pos, y_idx_to_pos, reverse=False
)

# Now we do the same to find the last shared index
last_shared_index, last_shared_pos_x, last_shared_pos_y = find_shared_index(
    sorted_x_indexes, sorted_y_indexes, x_idx_to_pos, y_idx_to_pos, reverse=True
)

# Select all indexes that come before (or include) this first shared index
candidate_indexes_start: set[int] = set()
candidate_indexes_end: set[int] = set()

# All indexes from sorted_x up to and including first shared
for i in range(first_shared_pos_x + 1):
    candidate_indexes_start.add(sorted_x_indexes[i])
# All indexes from sorted_y up to and including first shared
for i in range(first_shared_pos_y + 1):
    candidate_indexes_start.add(sorted_y_indexes[i])

# All indexes from sorted_x from last shared to end
for i in range(last_shared_pos_x, len(sorted_x_indexes)):
    candidate_indexes_end.add(sorted_x_indexes[i])
# All indexes from sorted_y from last shared to end
for i in range(last_shared_pos_y, len(sorted_y_indexes)):
    candidate_indexes_end.add(sorted_y_indexes[i])

print(f"Number of candidate indexes: {len(candidate_indexes_start)} start, {len(candidate_indexes_end)} end")
print(f"Total candidate combinations: {len(candidate_indexes_start) * len(candidate_indexes_end)}/{len(coordinates) * len(coordinates)}")
print(f"That's a reduction of {(1 - (len(candidate_indexes_start) * len(candidate_indexes_end)) / (len(coordinates) * len(coordinates))) * 100:.2f}%!")

# Now test all pairs of candidate indexes
max_area_approach2 = 0
best_idx1 = -1
best_idx2 = -1

candidate_list_start = list(candidate_indexes_start)
candidate_list_end = list(candidate_indexes_end)
for idx1 in candidate_list_start:
    for idx2 in candidate_list_end:

        x1, y1 = coordinates[idx1]
        x2, y2 = coordinates[idx2]

        # Calculate area
        area = (abs(x2 - x1) + 1) * (abs(y2 - y1) + 1)

        if area > max_area_approach2:
            max_area_approach2 = area
            best_idx1 = idx1
            best_idx2 = idx2

end_time_approach2 = perf_counter()
print(f"\nExecution time: {end_time_approach2 - start_time_approach2:.6f} seconds")

print(f"\n=== RESULTS ===")
print(f"Corner 1 coordinates: {coordinates[best_idx1]}")
print(f"Corner 2 coordinates: {coordinates[best_idx2]}")
print(f"Corner 1 shared index coordinate: {coordinates[first_shared_index]}")
print(f"Corner 2 shared index coordinate: {coordinates[last_shared_index]}")
print(f"Largest area found: {max_area_approach2}")

print(f"\n=== COMPARISON ===")
print(f"Approach 1 max area: {max_area_approach1}")
print(f"Approach 2 max area: {max_area_approach2}")
print(f"Results match: {max_area_approach1 == max_area_approach2}")
print(f"Approach 1 time: {end_time_approach1 - start_time_approach1:.6f} seconds")
print(f"Approach 2 time: {end_time_approach2 - start_time_approach2:.6f} seconds")
print(f"Approach 2 is {(end_time_approach1 - start_time_approach1) / (end_time_approach2 - start_time_approach2):.2f}x faster than Approach 1")