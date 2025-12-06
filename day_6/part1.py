# Read input from file
file = open("./input.txt", "r")

# I can only think of trivially creating a list per line
# and zipping through them
all_lines = [[item.strip() for item in line.rstrip().split(" ") if item.strip()] for line in file.readlines()]

# Iterate through each column
total = 0
num_columns = len(all_lines[0])
for col in range(num_columns):
    column_items = [all_lines[row][col] for row in range(len(all_lines))]
    operator = column_items[-1]
    if operator == "+":
        result = sum(int(item) for item in column_items[:-1])
    elif operator == "*":
        result = 1
        for item in column_items[:-1]:
            result *= int(item)
    else:
        raise ValueError(f"Unknown operator: {operator}")
    total += result
    print(f"Result of column {col + 1} ({operator}): {result}")

print(f"Total sum of all columns: {total}")