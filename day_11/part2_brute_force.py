from __future__ import annotations
from functools import lru_cache

# Read input from file
file = open("./input.txt", "r")
# Line example:   you: mdr yoa iwp ijc cjd

# We have a tree, now starting from 'svr', where each node branches to other devices
# sometimes we get from device A to device B in multiple ways, the end goal is
# to get to device 'out'. We need to find every possible path from 'svr' to 'out'.
# We should consider 'looping' behaviour where we can get from svr, back to svr.
# I'll assume we want to skip these, and not count them as valid paths.
# We now have an additional requirement that paths MUST flow through 'dac' AND 'fft'.
# The order doesn't matter, and as we're skipping loops, they should only be visited once
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

# There is a single starting point, 'svr', and multiple possible end points, 'out'.
start_device = devices.get("svr")
assert start_device is not None, "Starting device 'svr' not found"
end_device_name = "out"

@lru_cache(maxsize=None)
def count_paths(current_device_name: str, path_visited: frozenset[str], required_remaining: frozenset[str]) -> int:
    if current_device_name == end_device_name:
        # Check if both 'dac' and 'fft' have been visited
        if len(required_remaining) == 0:
            return 1
        else:
            return 0

    current_device = devices[current_device_name]
    total_paths = 0

    for conn in current_device.connections:
        if conn.name not in path_visited:
            new_path_visited = path_visited | {conn.name}
            new_required = required_remaining - {conn.name}
            total_paths += count_paths(conn.name, new_path_visited, new_required)

    return total_paths

total_paths = count_paths(start_device.name, frozenset({start_device.name}), frozenset({'dac', 'fft'}))
print(f"Total distinct paths from 'svr' to 'out': {total_paths}")
