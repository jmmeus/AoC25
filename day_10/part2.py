from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter

# Read input from file
file = open("./input.txt", "r")

# Example input line: [###.#] (2,3) (0,2,4) (0,2,3,4) (0,1,2,4) {201,19,208,185,201}
# Format here is: [lights] button1 button2 ... buttonN {joltage}
@dataclass
class InputLine:
    lights_goal: list[bool]
    lights_len: int
    buttons: list[tuple[int, ...]]
    joltage: list[int]

# ### Approach: Rational Gaussian Elimination ###
# We solve the linear system B * x = J (mod 2), where:
# - B is an N x M matrix (N lights, M buttons)
# - x is a vector of button press counts (must be non-negative, real integers)
# - J is the target joltage vector
# We want to minimize sum(x).
#
# Since standard methods (matrix inversion, simplex) don't guarantee integer solutions,
# we use Gaussian elimination with exact fraction arithmetic to:
# 1. Reduce the system to RREF (Row Reduced Echelon Form)
# 2. Identify pivot variables (dependent) and free variables (independent)
# 3. Express pivot variables as linear combinations of free variables
# 4. Use BFS to search free variable assignments by increasing total cost
# 5. For each assignment, check if pivot variables are non-negative integers
# 6. First valid solution found is optimal (due to BFS ordering)
# Thank you Adam for setting on this path :)

class Fraction:
    """Exact rational arithmetic using (numerator, denominator) pairs"""
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero")
        # Keep denominator positive, sign goes with numerator
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator
        # Reduce to lowest terms
        g = self._gcd(abs(numerator), abs(denominator))
        self.num = numerator // g
        self.den = denominator // g

    @staticmethod
    def _gcd(a: int, b: int) -> int:
        """Euclidean algorithm for greatest common divisor"""
        while b:
            a, b = b, a % b
        return a

    def __add__(self, other: Fraction) -> Fraction:
        return Fraction(
            self.num * other.den + other.num * self.den,
            self.den * other.den
        )

    def __sub__(self, other: Fraction) -> Fraction:
        return Fraction(
            self.num * other.den - other.num * self.den,
            self.den * other.den
        )

    def __mul__(self, other: Fraction) -> Fraction:
        return Fraction(self.num * other.num, self.den * other.den)

    def __truediv__(self, other: Fraction) -> Fraction:
        if other.num == 0:
            raise ValueError("Division by zero")
        return Fraction(self.num * other.den, self.den * other.num)

    def __neg__(self) -> Fraction:
        return Fraction(-self.num, self.den)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fraction):
            return NotImplemented
        return self.num == other.num and self.den == other.den

    def __lt__(self, other: Fraction) -> bool:
        return self.num * other.den < other.num * self.den

    def __le__(self, other: Fraction) -> bool:
        return self.num * other.den <= other.num * self.den

    def __gt__(self, other: Fraction) -> bool:
        return self.num * other.den > other.num * self.den

    def __ge__(self, other: Fraction) -> bool:
        return self.num * other.den >= other.num * self.den

    def is_zero(self) -> bool:
        return self.num == 0

    def is_integer(self) -> bool:
        """Check if this fraction represents an integer"""
        return self.den == 1

    def to_int(self) -> int:
        """Convert to integer (only call if is_integer() is True)"""
        if not self.is_integer():
            raise ValueError(f"Fraction {self.num}/{self.den} is not an integer")
        return self.num

    def __repr__(self) -> str:
        if self.den == 1:
            return str(self.num)
        return f"{self.num}/{self.den}"


def gauss_eliminate(B: list[list[int]], J: list[int]) -> list[list[Fraction]]:
    """
    Perform Gaussian elimination to Row Reduced Echelon Form (RREF).

    Input:
    - B: N x M matrix (coefficients)
    - J: N x 1 vector (constants)

    Output:
    - Augmented matrix [B | J] in RREF using exact fraction arithmetic
    """
    N = len(B)  # Number of equations (lights)
    M = len(B[0]) if N > 0 else 0  # Number of variables (buttons)

    # Create augmented matrix [B | J] with fractions
    aug: list[list[Fraction]] = []
    for i in range(N):
        row = [Fraction(B[i][j]) for j in range(M)]
        row.append(Fraction(J[i]))
        aug.append(row)

    current_row = 0

    # Forward elimination: create leading 1s and zeros below
    for col in range(M):
        # Find pivot (first non-zero entry in this column at or below current_row)
        pivot_row = None
        for row in range(current_row, N):
            if not aug[row][col].is_zero():
                pivot_row = row
                break

        if pivot_row is None:
            # No pivot in this column, it's a free variable
            continue

        # Swap rows if needed
        if pivot_row != current_row:
            aug[current_row], aug[pivot_row] = aug[pivot_row], aug[current_row]

        # Scale row to make pivot = 1
        pivot = aug[current_row][col]
        for j in range(M + 1):
            aug[current_row][j] = aug[current_row][j] / pivot

        # Eliminate column entries below pivot
        for row in range(current_row + 1, N):
            factor = aug[row][col]
            for j in range(M + 1):
                aug[row][j] = aug[row][j] - factor * aug[current_row][j]

        current_row += 1

    # Backward elimination: create zeros above pivots
    for row in range(min(current_row, N) - 1, -1, -1):
        # Find pivot column in this row
        pivot_col = None
        for col in range(M):
            if not aug[row][col].is_zero():
                pivot_col = col
                break

        if pivot_col is None:
            continue

        # Eliminate column entries above pivot
        for above_row in range(row):
            factor = aug[above_row][pivot_col]
            for j in range(M + 1):
                aug[above_row][j] = aug[above_row][j] - factor * aug[row][j]

    return aug


def extract_solution_structure(rref: list[list[Fraction]], M: int) -> tuple[list[int], list[int], dict[int, tuple[Fraction, dict[int, Fraction]]]]:
    """
    Extract pivot and free variables from RREF matrix.

    Returns:
    - pivot_vars: List of pivot variable indices
    - free_vars: List of free variable indices
    - pivot_equations: Dict mapping pivot_var -> (constant, {free_var: coefficient})
    """
    N = len(rref)
    pivot_vars: list[int] = []
    pivot_equations: dict[int, tuple[Fraction, dict[int, Fraction]]] = {}

    # Identify pivot columns
    for row in range(N):
        pivot_col = None
        for col in range(M):
            if not rref[row][col].is_zero():
                pivot_col = col
                break

        if pivot_col is not None:
            pivot_vars.append(pivot_col)

            # Extract equation: x_pivot = constant - sum(coeff * x_free)
            constant = rref[row][M]  # Last column is the constant term
            free_coeffs: dict[int, Fraction] = {}

            for col in range(pivot_col + 1, M):
                if not rref[row][col].is_zero():
                    # x_pivot + coeff * x_free = constant
                    # => x_pivot = constant - coeff * x_free
                    free_coeffs[col] = -rref[row][col]

            pivot_equations[pivot_col] = (constant, free_coeffs)

    # Free variables are those not in pivot_vars
    free_vars = [i for i in range(M) if i not in pivot_vars]

    return pivot_vars, free_vars, pivot_equations


class Queue:
    """Simple FIFO queue implementation for BFS traversal"""
    def __init__(self):
        self.items: list[tuple[int, ...]] = []
        self.front_index: int = 0

    def enqueue(self, item: tuple[int, ...]):
        self.items.append(item)

    def dequeue(self) -> tuple[int, ...]:
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


def find_minimum_presses(
    free_vars: list[int],
    pivot_equations: dict[int, tuple[Fraction, dict[int, Fraction]]],
    M: int,
    max_search_bound: int = 100
) -> int | None:
    """
    Use BFS to find the minimum button presses by exploring free variable assignments.

    We explore the space of free variable assignments, calculating the actual total cost
    (including pivot variables) for each. We track the minimum valid solution across
    all explored states.

    Args:
        free_vars: List of free variable indices
        pivot_equations: Mapping of pivot_var -> (constant, {free_var: coefficient})
        M: Total number of variables (buttons)
        max_search_bound: Maximum value for any single free variable

    Returns:
        Minimum total button presses, or None if no valid solution exists
    """
    if len(free_vars) == 0:
        # No free variables, unique solution
        # Check if all pivot variables are non-negative integers
        solution = [Fraction(0)] * M
        for pivot_var, (constant, _) in pivot_equations.items():
            if not constant.is_integer() or constant < Fraction(0):
                return None
            solution[pivot_var] = constant
        return sum(s.to_int() for s in solution)

    def calculate_total_cost(free_assignment: tuple[int, ...]) -> int | None:
        """Calculate total cost for a given free variable assignment, or None if invalid"""
        solution = [Fraction(0)] * M
        for i, free_var in enumerate(free_vars):
            solution[free_var] = Fraction(free_assignment[i])

        # Calculate pivot variables
        for pivot_var, (constant, free_coeffs) in pivot_equations.items():
            value = constant
            for free_var, coeff in free_coeffs.items():
                value = value + coeff * solution[free_var]

            # Check if value is a non-negative integer
            if not value.is_integer() or value < Fraction(0):
                return None

            solution[pivot_var] = value

        return sum(s.to_int() for s in solution)

    # Use BFS to explore free variable assignments, tracking the minimum valid solution
    queue = Queue()
    visited: set[tuple[int, ...]] = set()

    best_cost: int | None = None

    # Start with initial assignment (all free vars = 0)
    initial_assignment = tuple(0 for _ in free_vars)
    queue.enqueue(initial_assignment)
    visited.add(initial_assignment)

    while not queue.is_empty():
        current = queue.dequeue()

        # Calculate cost for this assignment
        cost = calculate_total_cost(current)

        if cost is not None:
            # Valid solution found
            if best_cost is None or cost < best_cost:
                best_cost = cost

        # Generate successors (increment each free variable)
        for i in range(len(free_vars)):
            new_assignment = list(current)
            new_assignment[i] += 1

            # Bound check
            if new_assignment[i] > max_search_bound:
                continue

            # Pruning: if sum of free vars alone exceeds best cost, skip
            if best_cost is not None and sum(new_assignment) >= best_cost:
                continue

            new_tuple = tuple(new_assignment)
            if new_tuple not in visited:
                visited.add(new_tuple)
                queue.enqueue(new_tuple)

    return best_cost


start_time = perf_counter()

# Process lines
lines: list[InputLine] = []
for raw_line in file:
    parts = raw_line.strip().split(" ")
    lights_str = parts[0][1:-1]
    lights_goal = [c == "#" for c in lights_str]
    lights_len = len(lights_str)
    buttons = [tuple(map(int, part[1:-1].split(","))) for part in parts[1:-1]]
    joltage = list(map(int, parts[-1][1:-1].split(",")))
    lines.append(InputLine(lights_goal, lights_len, buttons, joltage))

# Solve each line using Gaussian elimination + BFS
min_total_presses = 0
for i, line in enumerate(lines):
    print(f"Processing line {i+1}/{len(lines)}")

    # Construct matrix B: B[light_idx][button_idx] = 1 if button affects light
    N = line.lights_len  # Number of lights (equations)
    M = len(line.buttons)  # Number of buttons (variables)
    B = [[0 for _ in range(M)] for _ in range(N)]
    for button_idx, button in enumerate(line.buttons):
        for light_idx in button:
            B[light_idx][button_idx] = 1

    # Target vector J: joltage for each light
    J = line.joltage

    # Perform Gaussian elimination to RREF
    rref = gauss_eliminate(B, J)

    # Check for inconsistency: row of zeros with non-zero constant
    for row in rref:
        all_zero_coeffs = all(row[col].is_zero() for col in range(M))
        if all_zero_coeffs and not row[M].is_zero():
            raise ValueError(f"No solution exists for line {i+1}")

    # Extract solution structure
    _, free_vars, pivot_equations = extract_solution_structure(rref, M)

    # Find minimum button presses using BFS
    result = find_minimum_presses(free_vars, pivot_equations, M, max_search_bound=500)

    if result is None:
        raise ValueError(f"No valid integer solution found for line {i+1}")

    print(f"  Solution: {result} button presses")
    min_total_presses += result

end_time = perf_counter()
print(f"Processed {len(lines)} lines in {end_time - start_time:.4f} seconds")
print(f"Minimum total presses: {min_total_presses}")
