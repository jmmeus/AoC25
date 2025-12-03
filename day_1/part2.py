from __future__ import annotations

# Create a WrappedInt class to handle the rollover/wrapping
# when value > 99 or value < 0
class WrappedInt:
    def __init__(self, value: int | float | str | WrappedInt):
        if isinstance(value, WrappedInt):
            self.value = value.value
        else:
            # Ensure value is valid integer
            try:
                value = int(value)
            except ValueError:
                raise ValueError("WrappedInt can only be initialized with an integer value.")
            
            # Apply rollover using modulo 100
            self.value = int(value) % 100

    def __add__(self, other: int):
        return WrappedInt(self.value + other)

    def __sub__(self, other: int):
        return WrappedInt(self.value - other)

    def __int__(self) -> int:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, WrappedInt):
            return self.value == other.value
        if isinstance(other, (int, float, str)):
            return self.value == int(other)
        raise NotImplementedError("Comparison not supported between WrappedInt and given type.")
    
    def __repr__(self) -> str:
        return f"WrappedInt({self.value})"

# Read input from file
file = open("day_1/input.txt", "r")

current_position = WrappedInt(50) # Starts at position 50
password = 0

for rotation in file.readlines():
    direction, count = rotation[0], rotation[1:]
    count = int(count)
    
    # If direction is "R", add, if "L", subtract
    raw_new_position = current_position.value + count if direction == "R" else current_position.value - count
    new_position = current_position + count if direction == "R" else current_position - count

    if raw_new_position == 0:
        # Landed exactly on 0, count as crossing
        password += 1
    elif raw_new_position != new_position:
        # Raw position differs from wrapped position, so we crossed 0
        password += abs(raw_new_position) // 100

        if raw_new_position < 0 and current_position != 0:
            # Wrapped around negatively (< 0) and didn't start at 0
            # Anything < (-)99 will floor divide to 0, so need to add 1
            # e.g. abs(-40) // 100 = 0, but we crossed 0 *to get into negatives*
            password += 1

    current_position = new_position

print(f"Password: {password}")