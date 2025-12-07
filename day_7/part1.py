# Read input from file
file = open("./input.txt", "r")

# We'll keep track of 'active' beam indexes (ie override each line)
# We'll use a set to avoid duplicates when splitting
beam_indexes: set[int] = set()

# First line holds 'S' as starting 'beam'
first_line: str = file.readline().rstrip()
if 'S' in first_line:
    beam_indexes = {first_line.index('S')}
else:
    # Not like this will happen
    raise ValueError("First line must contain starting 'S'")

split_count = 0
_line_count = 1
# Process remaining line by line
for line in file:
    # print(f"Processing line {_line_count}")
    _line_count += 1
    line = line.rstrip()
    new_beam_indexes: set[int] = set()
    for index in beam_indexes:
        if line[index] == '^':
            # Beam is split, go left and right
            if index - 1 >= 0: # Just check bounds // go left
                new_beam_indexes.add(index - 1)
            if index + 1 < len(line): # Just check bounds // go right
                new_beam_indexes.add(index + 1)
            split_count += 1
        else: # line[index] == '.'
            # Beam continues straight down
            new_beam_indexes.add(index)
    
    # Update beam indexes for next line
    beam_indexes = new_beam_indexes

print(f"Number of splits encountered: {split_count}")