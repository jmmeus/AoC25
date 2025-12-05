from typing import Literal
from time import perf_counter
import tracemalloc
import os

# Read input from file
file = open("./input.txt", "r")

# Now, we do this 'iteratively' until no more changes occur
# This would be trivial with the whole grid in memory but where's the fun in that?
# I attempted to keep this line-by-line, but there is no way to ensure that
# A change in the last line won't affect the first line
# I considered a recursive generator approach, but this would
# potentially run into recursion limits for large inputs

# Instead, we'll just continuously loop through the file,
# storing only the changes as a set (for O(1) lookups), and
# apply the changes during each iteration until no more changes occur
# This is likely more memory intensive that just stroing the raw string input,
# but it was fun to implement

def count_adjacent_at_signs(relative_row: int, col: int) -> int:
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  ( 0, -1),          ( 0, 1),
                  ( 1, -1), ( 1, 0), ( 1, 1)]
    count = 0
    for dr, dc in directions:
        r, c = relative_row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < len(current_line):
            if (r == 0 and previous_line[c] == '@') or \
               (r == 1 and current_line[c] == '@') or \
               (r == 2 and next_line[c] == '@'):
                count += 1
    return count

# tracemalloc adds significant overhead, so simultaneous benchmarking is not accurate
# Read benchmark type from environment with in-file default fallback
BENCHMARK_TYPE: Literal["MEMORY", "TIME"] = os.environ.get("BENCHMARK", "TIME")  # type: ignore

if BENCHMARK_TYPE == "MEMORY": # type: ignore
    tracemalloc.start()

NEIGHBOUR_THRESHOLD: Literal[4] = 4
changes: bool = True
all_changes: set[tuple[int, int]] = set()
total_count_iterative: int = 0 # Keeping to ensure no duplicates, trivially len(all_changes)

if BENCHMARK_TYPE == "TIME":
    start_time = perf_counter()

while changes:
    changes = False

    # Reset file to start
    file.seek(0)
    first_line = file.readline().rstrip()
    previous_line = ['.' for _ in first_line]
    current_line = ['.' for _ in first_line]
    next_line = list(first_line)
    line_counter: int = -1 # Keep track of current line number

    for line in file:
        line = line.rstrip()
        # Shift lines, and apply changes
        previous_line = current_line
        current_line = next_line
        next_line = list(line)

        line_counter += 1

        # Previous line row = line_counter - 1 (if line_counter > 0, otherwise this line is a placeholder anyway)
        # Current line row = line_counter
        # Next line row = line_counter + 1 (if line_counter < total_lines - 1, but this will only happen outside the loop)
        
        # Apply all changes to the three lines
        for row_offset, line_data in [(-1, previous_line), (0, current_line), (1, next_line)]:
            row = line_counter + row_offset
            if row < 0:
                continue  # Out of bounds, skip
            for col in range(len(line_data)):
                if (row, col) in all_changes:
                    # Apply change
                    line_data[col] = 'x'
        
        # Now process the current_line
        for col in range(len(current_line)):
            if current_line[col] == '@':
                adjacent_count = count_adjacent_at_signs(1, col)
                if adjacent_count < NEIGHBOUR_THRESHOLD:
                    total_count_iterative += 1
                    changes = True
                    all_changes.add((line_counter, col))

    # Process the last line after the loop
    previous_line = current_line
    current_line = next_line
    next_line = ['.' for _ in first_line]

    line_counter += 1

    # Apply all changes to the "three" lines // Can skip next_line as it's placeholder here
    for row_offset, line_data in [(-1, previous_line), (0, current_line)]:
        row = line_counter + row_offset
        for col in range(len(line_data)):
            if (row, col) in all_changes:
                # Apply change
                line_data[col] = 'x'

    for col in range(len(current_line)):
        if current_line[col] == '@':
            adjacent_count = count_adjacent_at_signs(1, col)
            if adjacent_count < NEIGHBOUR_THRESHOLD:
                total_count_iterative += 1
                changes = True
                all_changes.add((line_counter, col))

if BENCHMARK_TYPE == "TIME":
    end_time = perf_counter()
    print(f"Iterative Execution time: {end_time - start_time:.6f} seconds") # type: ignore
elif BENCHMARK_TYPE == "MEMORY":
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")


print(f"Total '@' characters with fewer than {NEIGHBOUR_THRESHOLD} adjacent '@' (iterative): {total_count_iterative} ({len(all_changes)} changes made)")

# Print the whole grid with changes applied
# file.seek(0)
# line_counter = -1
# for line in file.readlines():
#     line = line.rstrip()
#     line_counter += 1
#     line_data = list(line)
#     for col in range(len(line_data)):
#         if (line_counter, col) in all_changes:
#             line_data[col] = 'x'
#     print("".join(line_data))
