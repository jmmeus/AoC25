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

# For task 2, we could use the BFS approach to find the minimum button presses
# to reach the joltage goal for each line. Unlike part 1, our state will be joltage
# counts, and a button press increments the index of each joltage in the button's tuple.
# Notably, we can stop tracking states where any of the joltages exceed the goal joltage,
# as those states cannot lead to a solution.
# // Investigating the input, some joltage values reach up to hundreds, with lengths of ~10,
# // and jumps of 1 per buttons press. The BFS will thus explore a massive state space.
# // e.g., for a joltage goal of {90,46,86,53,31,94,57,80,66,58}, the state space volume
# // is 90*46*86*53*31*94*57*80*66*58 ~ 1e18 states, with jumps of 1 in 10 dimensions,
# // we have ~1e18 / 1^10 = 1e18 states to explore, which is stupidly large.
# It does however work, and correctly gives 33 for the example input in ~0.01s.
class State:
    def __init__(self, joltage: tuple[int, ...], presses: int):
        self.joltage = joltage
        self.presses = presses

    # We'll need hash and eq methods to store in a set
    # without this, we lose performance drastically as
    # Python will use the default object hash/eq
    # which is based on object identity not values
    # and thus every state will be unique
    def __hash__(self):
        return hash(self.joltage)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            raise NotImplementedError("Comparison is only supported between State instances")
        return self.joltage == other.joltage
    
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
    
    def size(self) -> int:
        return len(self.items) - self.front_index

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
    initial_state = tuple(0 for _ in range(line.lights_len))
    goal_state = tuple(line.joltage)

    initial = State(initial_state, 0)
    queue = Queue()
    queue.enqueue(initial)
    visited: set[State] = set()
    visited.add(initial)
    found_presses: int | None = None
    while not queue.is_empty():
        # print(f"  Queue size: {queue.size()}")
        # print(f'  Processing state: {queue.items[queue.front_index].joltage} with presses {queue.items[queue.front_index].presses}')
        current = queue.dequeue()
        if current.joltage == goal_state:
            found_presses = current.presses
            break
        
        for button in line.buttons:
            new_joltage = list(current.joltage)
            for index in button:
                new_joltage[index] += 1
            new_state = State(tuple(new_joltage), current.presses + 1)
            # Prune states that exceed goal joltage
            if any(new_joltage[i] > goal_state[i] for i in range(line.lights_len)):
                continue
            if new_state not in visited:
                visited.add(new_state)
                queue.enqueue(new_state)

    if found_presses is None:
        raise ValueError(f"!!! No solution found for line {i} !!!")
    min_total_presses += found_presses

end_time = perf_counter()
print(f"Processed {len(lines)} lines in {end_time - start_time:.4f} seconds")

print(f"Minimum total presses: {min_total_presses}")
