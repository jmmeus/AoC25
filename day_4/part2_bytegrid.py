from typing import Literal
from time import perf_counter
import tracemalloc
import os

# Simple queue implementation to avoid external dep
class Queue:
    """Simple FIFO queue implementation for BFS traversal"""
    def __init__(self):
        self.items: list[int] = []
        self.front_index: int = 0

    def append(self, item: int) -> None:
        self.items.append(item)

    def popleft(self) -> int:
        if self.is_empty():
            raise IndexError("pop from empty queue")
        item = self.items[self.front_index]
        self.front_index += 1
        # Periodically clean up consumed items to prevent memory bloat
        if self.front_index > 1000:
            self.items = self.items[self.front_index:]
            self.front_index = 0
        return item

    def is_empty(self) -> bool:
        return self.front_index >= len(self.items)

# Two-pass queue-based approach WITH byte grid optimization
#
# Optimization 1 (Algorithmic): Instead of repeatedly scanning the entire grid
# se a queue-based cascade (see part2_optimised.py).
#
# Optimization 2 (Memory): We use a flat bytearray instead of nested lists,
# storing both "paper present" flag and neighbor count in a single byte using
# bit manipulation. This provides better cache locality and reduces memory overhead.
# We'll use bits 0-3 for neighbor count (0-8) and bit 7 for paper presence. This gives
# us a 'safety net' in bits 4-6 in case of bugs (eg the count exceeds 8), without affecting
# correctness.
#
# Byte layout per cell:
#   Bit 7 (0x80): Paper present flag (1 = paper exists, 0 = removed)
#   Bits 0-3 (0x0F): Neighbor count (0-8)
#
# The thinking: The two-pass approach eliminates redundant scans, while the byte
# grid reduces memory footprint from Python objects to raw bytes, improving both
# speed (cache efficiency) and memory usage // Notably it seems this is not actually
# faster than the list version, likely due to the increased bit manipulation overhead?

# Constants for bit manipulation
PAPER_BIT: int = 0b10000000  # Bit 7: Paper present flag (128)
COUNT_MASK: int = 0b00001111  # Bits 0-3: Neighbor count mask (15)

# Read benchmark type from environment
BENCHMARK_TYPE: Literal["MEMORY", "TIME"] = os.environ.get("BENCHMARK", "TIME")  # type: ignore

if BENCHMARK_TYPE == "MEMORY":
    tracemalloc.start()

NEIGHBOUR_THRESHOLD: Literal[4] = 4

# Read input from file and build bytearray line-by-line (integrated Pass 1)
file = open("./input.txt", "r")

# Start timing BEFORE processing (includes file read loop)
if BENCHMARK_TYPE == "TIME":
    start_time = perf_counter()

# Pass 1: Read file line-by-line and set "Paper Present" flag
# This eliminates the need to store the entire file as strings in memory
grid = bytearray()
height = 0
width = 0

for line in file:
    line = line.rstrip()
    if height == 0:  # First line determines width
        width = len(line)
    height += 1

    # Immediately convert each character to byte with PAPER_BIT set
    for c in line:
        if c == '@':
            grid.append(PAPER_BIT)
        else:
            grid.append(0)

file.close()

# Pass 2: Calculate neighbor counts and initialize queue
queue = Queue()
directions = [(-1, -1), (-1, 0), (-1, 1),
              ( 0, -1),          ( 0, 1),
              ( 1, -1), ( 1, 0), ( 1, 1)]

for r in range(height):
    for c in range(width):
        idx = r * width + c

        # Check if paper is present (Bit 7 is set)
        if grid[idx] & PAPER_BIT:
            count = 0
            # Count neighbors with paper
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < height and 0 <= nc < width:
                    # Check if neighbor has paper (Bit 7 is set)
                    if grid[nr * width + nc] & PAPER_BIT:
                        count += 1

            # Store count in bits 0-3 (OR with PAPER_BIT to preserve it)
            grid[idx] |= count

            # If removable immediately, add to queue
            if count < NEIGHBOUR_THRESHOLD:
                queue.append(idx)

# BFS: Remove cells and cascade updates to neighbors
removed_total = 0

while not queue.is_empty():
    curr_idx = queue.popleft()

    # Ensure paper is still present (Bit 7 is set)
    if not (grid[curr_idx] & PAPER_BIT):
        continue

    # Remove paper: Turn off Bit 7 using AND with inverted mask
    grid[curr_idx] &= ~PAPER_BIT
    removed_total += 1

    # Calculate coordinates to find neighbors
    r, c = divmod(curr_idx, width)

    # Update all 8 neighbors
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < height and 0 <= nc < width:
            n_idx = nr * width + nc

            # Check if neighbor has paper (Bit 7 is set)
            if grid[n_idx] & PAPER_BIT:
                # Decrement neighbor count (bits 0-3)
                grid[n_idx] -= 1

                # Extract just the count to check threshold
                current_neighbor_count = grid[n_idx] & COUNT_MASK

                # If neighbor just became removable (dropped to 3), queue it
                if current_neighbor_count == NEIGHBOUR_THRESHOLD - 1:
                    queue.append(n_idx)

if BENCHMARK_TYPE == "TIME":
    end_time = perf_counter()
    print(f"ByteGrid Execution time: {end_time - start_time:.6f} seconds") # type: ignore
elif BENCHMARK_TYPE == "MEMORY":
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")

print(f"Total '@' characters with fewer than {NEIGHBOUR_THRESHOLD} adjacent '@' (bytegrid): {removed_total}")
