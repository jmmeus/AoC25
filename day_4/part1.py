# Read input from file
file = open("./input.txt", "r")

# Our input is a 2D grid of . and @ characters
# Each line needs only neighbouring lines to check
# So we can read line by line and keep only the last line in memory
# We will count the number of '@' characters that are adjacent (including diagonals)
# to any other '@' character
# We consider adjacency in 8 directions (N, NE, E, SE, S, SW, W, NW)
# We will use a sliding window of 3 lines to do this
# Just before 'deleting' the oldest line, we count the number of @ characters
# that have < N @ neighbours

first_line = file.readline().rstrip()

NEIGHBOUR_THRESHOLD = 4
previous_line: list[str] = ['.' for _ in first_line]
current_line: list[str] = ['.' for _ in first_line]
next_line: list[str] = list(first_line)
total_count = 0

def count_adjacent_at_signs(row: int, col: int) -> int:
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  ( 0, -1),          ( 0, 1),
                  ( 1, -1), ( 1, 0), ( 1, 1)]
    count = 0
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < len(current_line):
            if (r == 0 and previous_line[c] == '@') or \
               (r == 1 and current_line[c] == '@') or \
               (r == 2 and next_line[c] == '@'):
                count += 1
    return count

for line in file.readlines():
    line = line.rstrip()
    # Shift lines
    previous_line = current_line
    current_line = next_line
    next_line = list(line)
    
    # Now process the current_line
    for col in range(len(current_line)):
        if current_line[col] == '@':
            adjacent_count = count_adjacent_at_signs(1, col)
            if adjacent_count < NEIGHBOUR_THRESHOLD:
                total_count += 1

# Process the last line after the loop
previous_line = current_line
current_line = next_line
next_line = ['.' for _ in first_line]

for col in range(len(current_line)):
    if current_line[col] == '@':
        adjacent_count = count_adjacent_at_signs(1, col)
        if adjacent_count < NEIGHBOUR_THRESHOLD:
            total_count += 1

print(f"Total '@' characters with fewer than {NEIGHBOUR_THRESHOLD} adjacent '@': {total_count}")

