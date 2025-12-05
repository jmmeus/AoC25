from typing import Literal
from time import perf_counter
import tracemalloc
import os

# Simple queue implementation to avoid external dep
class Queue:
    """Simple FIFO queue implementation for BFS traversal"""
    def __init__(self):
        self.items: list[tuple[int, int]] = []
        self.front_index: int = 0

    def append(self, item: tuple[int, int]) -> None:
        self.items.append(item)

    def popleft(self) -> tuple[int, int]:
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

# Two-pass queue-based approach:
# Instead of repeatedly scanning the entire grid until no changes occur (O(n^2 × k)),
# we can use a queue-based cascade that visits each cell at most once for removal,
# achieving O(n)
#
# When a cell is removed, only its 8 neighbors are affected, if we track neighbor counts 
# and queue cells when they become removable, we eliminate redundant grid scans and 
# process removal in a single pass.

# Read benchmark type from environment
BENCHMARK_TYPE: Literal["MEMORY", "TIME"] = os.environ.get("BENCHMARK", "TIME")  # type: ignore

if BENCHMARK_TYPE == "MEMORY":
    tracemalloc.start()

NEIGHBOUR_THRESHOLD: Literal[4] = 4

# Read input from file
file = open("./input.txt", "r")
lines = [line.rstrip() for line in file.readlines()]
file.close()

# Start timing/memory AFTER file read, BEFORE processing
if BENCHMARK_TYPE == "TIME":
    start_time = perf_counter()

H, W = len(lines), len(lines[0]) if lines else 0

# Pass 1: Parse grid and identify all '@' positions
# Store as list[list[int]] where value represents:
# -1 = no paper, >= 0 = neighbor count (paper present)
grid: list[list[int]] = []
for r in range(H):
    row: list[int] = []
    for c in range(W):
        if lines[r][c] == '@':
            row.append(0)  # Paper present, count will be calculated in pass 2
        else:
            row.append(-1)  # No paper
    grid.append(row)

# Pass 2: Calculate neighbor counts and initialize queue
queue = Queue()
directions = [(-1, -1), (-1, 0), (-1, 1),
              ( 0, -1),          ( 0, 1),
              ( 1, -1), ( 1, 0), ( 1, 1)]

for r in range(H):
    for c in range(W):
        if grid[r][c] >= 0:  # Paper present
            count = 0
            # Count neighbors with paper
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < H and 0 <= nc < W:
                    if grid[nr][nc] >= 0:  # Neighbor has paper
                        count += 1

            grid[r][c] = count

            # If removable immediately, add to queue
            if count < NEIGHBOUR_THRESHOLD:
                queue.append((r, c))

# BFS: Remove cells and cascade updates
removed_total = 0

while not queue.is_empty():
    r, c = queue.popleft()

    # Ensure paper is still present
    if grid[r][c] < 0:
        continue

    # Remove paper // mark as removed
    grid[r][c] = -1
    removed_total += 1

    # Update all 8 neighbors
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < H and 0 <= nc < W:
            if grid[nr][nc] >= 0:  # Neighbor has paper
                grid[nr][nc] -= 1

                # If neighbor just became removable (dropped to 3), queue it
                # Note that we don't need to check for < threshold, only == threshold - 1
                # as < threshold have been added to the queue already
                if grid[nr][nc] == NEIGHBOUR_THRESHOLD - 1:
                    queue.append((nr, nc))

if BENCHMARK_TYPE == "TIME":
    end_time = perf_counter()
    print(f"Two-Pass Queue Execution time: {end_time - start_time:.6f} seconds") # type: ignore
elif BENCHMARK_TYPE == "MEMORY":
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")

print(f"Total '@' characters with fewer than {NEIGHBOUR_THRESHOLD} adjacent '@' (two-pass): {removed_total}")
