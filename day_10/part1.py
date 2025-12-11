from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter

# Read input from file
file = open("./input.txt", "r")

# Example input line: [###.#] (2,3) (0,2,4) (0,2,3,4) (0,1,2,4) {201,19,208,185,201}
# Format here is: [lights] button1 button2 ... buttonN {joltage}
# Lets use a dataclass to store each line's data
@dataclass
class InputLine:
    lights_goal: list[bool]
    lights_len: int
    buttons: list[tuple[int, ...]]
    joltage: list[int]

# For this task, it's just a 'boring' BFS to explore light states for
# different button presses. We can ignore the joltage for now.
# Notably, we'll define a state to be the lights configuration, and
# cache visited states to avoid reprocessing them. We won't need to track
# the button presses themselves, just the count of presses to reach a state.
class State:
    def __init__(self, lights: tuple[bool, ...], presses: int):
        self.lights = lights
        self.presses = presses

    # We'll need hash and eq methods to store in a set
    # without this, we lose performance drastically as
    # Python will use the default object hash/eq
    # which is based on object identity not values
    # and thus every state will be unique
    def __hash__(self):
        return hash(self.lights)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            raise NotImplementedError("Comparison is only supported between State instances")
        return self.lights == other.lights
    
# I can reuse my Queue from day 4's optimised approach
class Queue:
    """Simple FIFO queue implementation for BFS traversal"""
    def __init__(self):
        self.items: list[State] = []
        self.front_index: int = 0

    def enqueue(self, item: State):
        self.items.append(item)

    def dequeue(self) -> State:
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

start_time = perf_counter()

# Process lines
lines: list[InputLine] = []
for raw_line in file:
    parts = raw_line.strip().split(" ")
    lights_str = parts[0][1:-1]
    lights_goal = [c == "#" for c in lights_str]
    lights_len = len(lights_str)
    buttons = [tuple(map(int, part[1:-1].split(","))) for part in parts[1:-1]]
    joltage = list(map(int, parts[-1][1:-1].split(",")))
    lines.append(InputLine(lights_goal, lights_len, buttons, joltage))

# Now perform BFS for each line to find minimum button presses
min_total_presses = 0
for i, line in enumerate(lines):
    # print(f"Processing line {i+1}/{len(lines)}")
    initial_state = tuple(False for _ in range(line.lights_len))
    goal_state = tuple(line.lights_goal)

    initial = State(initial_state, 0)
    queue = Queue()
    queue.enqueue(initial)
    visited: set[State] = set()
    visited.add(initial)
    found_presses: int | None = None
    while not queue.is_empty():
        current = queue.dequeue()
        if current.lights == goal_state:
            found_presses = current.presses
            break
        
        for button in line.buttons:
            new_lights = list(current.lights)
            for index in button:
                new_lights[index] = not new_lights[index]
            new_state = State(tuple(new_lights), current.presses + 1)
            if new_state not in visited:
                visited.add(new_state)
                queue.enqueue(new_state)

    if found_presses is None:
        raise ValueError(f"!!! No solution found for line {i} !!!")
    min_total_presses += found_presses

end_time = perf_counter()
print(f"Processed {len(lines)} lines in {end_time - start_time:.4f} seconds")

print(f"Minimum total presses: {min_total_presses}")
