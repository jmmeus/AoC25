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
    current_position = current_position + count if direction == "R" else current_position - count

    if current_position == 0:
        password += 1

print(f"Password: {password}")