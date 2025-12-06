# Read input from file
with open("./input.txt", "r") as file:
    # Parse input character by character per line (numbers are arranged vertically)
    all_lines = [[char for char in line.rstrip()] for line in file]

# Pad lines to max length with spaces (some lines are shorter than others)
max_length = max(len(line) for line in all_lines)
all_lines = [line + [" "] * (max_length - len(line)) for line in all_lines]

# Function to process a column group
def process_column_group(column_group: list[str]) -> int:
    """Calculate result for a column group based on operator."""
    operator = '*' if '*' in column_group else '+'
    nums = [int(num) for num in column_group if num not in "+*"]
    if operator == "+":
        return sum(nums)
    else:  # operator == "*"
        result = 1
        for num in nums:
            result *= num
        return result

# Iterate through columns and calculate total
# Numbers are arranged vertically, so we group columns until hitting a full ' ' column
total = 0
num_columns = len(all_lines[0])
latest_column: list[str] = []

for col in range(num_columns):
    # Extract all items in this column
    column_items = [all_lines[row][col] for row in range(len(all_lines))]
    
    # Check if we hit a separator column (all spaces)
    if all(item == " " for item in column_items):
        # Process the column group
        if latest_column:
            result = process_column_group(latest_column)
            total += result
            print(f"Calculation was {latest_column}, Result: {result}")
            latest_column = []
    # Check if column contains an operator
    elif '*' in column_items or '+' in column_items:
        operator = '*' if '*' in column_items else '+'
        latest_column.append("".join(column_items).strip().rstrip(operator))
        latest_column.append(operator)
    else:
        # Regular number column
        latest_column.append("".join(column_items).strip())

# Process remaining column group
if latest_column:
    result = process_column_group(latest_column)
    total += result
    print(f"Calculation was {latest_column}, Result: {result}")

print(f"Total sum of all columns: {total}")

# By visually observing the input, it would potentially be easier to parse columns based on
# operators, as these seem to always be in 'column 1' for a new operation.
