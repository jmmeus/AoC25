from __future__ import annotations

# Read input from file
file = open("./input.txt", "r")
# Line example:   svr: mdr yoa iwp ijc cjd

# We have a DAG starting from 'svr' with goal 'out'.
# Paths must visit BOTH 'dac' AND 'fft' (order doesn't matter).
# Each node visited at most once per path.
#
# Strategy: Since order doesn't matter, we have two possible sequences:
# - Sequence A: svr → fft → dac → out
# - Sequence B: svr → dac → fft → out
#
# For each sequence, we compute the product of path counts between consecutive waypoints.
# Since it's a DAG, these segment counts are independent and can be multiplied.
# The total is the sum of both sequences.

class Device:
    def __init__(self, name: str):
        self.name = name
        self.connections: list[Device] = []

    def add_connection(self, device: Device):
        self.connections.append(device)


devices: dict[str, Device] = {}

for line in file:
    parts = line.strip().split(":")
    device_name = parts[0].strip()
    connections = parts[1].strip().split() if len(parts) > 1 else []

    if device_name not in devices:
        devices[device_name] = Device(device_name)

    for conn_name in connections:
        if conn_name not in devices:
            devices[conn_name] = Device(conn_name)
        devices[device_name].add_connection(devices[conn_name])

# Validate required devices exist
assert "svr" in devices, "Starting device 'svr' not found"
assert "out" in devices, "End device 'out' not found"
assert "dac" in devices, "Required device 'dac' not found"
assert "fft" in devices, "Required device 'fft' not found"


def count_segment_paths(start_name: str, end_name: str) -> int:
    """
    Count all paths from start to end in the DAG.

    Uses DFS with manual memoization. The cache key is just the current node,
    which works in a DAG because we don't need to track visited nodes -
    the acyclic structure ensures we can't loop back.
    """
    cache: dict[str, int] = {}

    def dfs(node_name: str) -> int:
        # Base case: reached the target
        if node_name == end_name:
            return 1

        # Check cache
        if node_name in cache:
            return cache[node_name]

        # Sum paths through all neighbors
        current_device = devices[node_name]
        total = 0
        for conn in current_device.connections:
            total += dfs(conn.name)

        # Store in cache
        cache[node_name] = total
        return total

    return dfs(start_name)


# Compute paths for both possible orderings of waypoints
# Sequence A: svr → fft → dac → out
paths_a = (
    count_segment_paths('svr', 'fft') *
    count_segment_paths('fft', 'dac') *
    count_segment_paths('dac', 'out')
)

# Sequence B: svr → dac → fft → out
paths_b = (
    count_segment_paths('svr', 'dac') *
    count_segment_paths('dac', 'fft') *
    count_segment_paths('fft', 'out')
)

print(f"Sequence A paths (svr → fft → dac → out): {paths_a}")
print(f"Sequence B paths (svr → dac → fft → out): {paths_b}")
# Notably, either Sequence A or B will be zero, as both must be visited,
# and loops are not allowed, so if fft -> dac exists, dac -/-> fft cannot.
# // spoiler: sequence B is zero in the actual input.

# Total paths is the sum of both sequences
total_paths = paths_a + paths_b
print(f"Total distinct paths from 'svr' to 'out': {total_paths}")
