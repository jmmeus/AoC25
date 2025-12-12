from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Condition:
    width: int
    length: int
    counts: list[int]

# Read input from file
file = open("./input.txt", "r")

shapes: list[list[str]] = []
conditions: list[Condition] = []

current_shape: list[str] = []
for line in file:
    line = line.strip()
    if line == "":
        continue
    if "x" not in line and ":" in line:
        if current_shape:
            shapes.append(current_shape)
            current_shape = []
    elif "x" in line and ":" in line:
        area_part, counts_part = line.split(":")
        width, length = map(int, area_part.split("x"))
        counts_list = counts_part.strip().split()
        counts = [int(count) for count in counts_list]
        conditions.append(Condition(width, length, counts))
    else:
        current_shape.append(line)

if current_shape:
    shapes.append(current_shape)

file.close()

# Calculate shape sizes
shape_sizes: list[int] = []
for shape in shapes:
    size = sum(row.count("#") for row in shape)
    shape_sizes.append(size)

# Check each condition
success_count = 0
for condition in conditions:
    available_area = condition.width * condition.length
    
    total_cells_needed = 0
    for shape_index, count in enumerate(condition.counts):
        total_cells_needed += shape_sizes[shape_index] * count
    
    if total_cells_needed <= available_area:
        success_count += 1

print(f"Number of successful conditions: {success_count}")

# Dirty work Eric. No christmas spirit at all :(