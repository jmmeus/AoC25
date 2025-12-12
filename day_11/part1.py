from __future__ import annotations

# Read input from file
file = open("./input.txt", "r")
# Line example:   you: mdr yoa iwp ijc cjd

# We have a tree, starting from 'you', where each node branches to other devices
# sometimes we get get from device A to device B in multiple ways, the end goal is
# to get to device 'out'. We need to find every possible path from 'you' to 'out'.
# We should consider 'looping' behaviour where we can get from you, back to you.
# I'll assume we want to skip these, and not count them as valid paths.
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

# There is a single starting point, 'you', and multiple possible end points, 'out'.
start_device = devices.get("you")
assert start_device is not None, "Starting device 'you' not found"
end_device_name = "out"

def count_paths(current_device: Device, visited: set[str]) -> int:
    if current_device.name == end_device_name:
        return 1

    total_paths = 0
    visited.add(current_device.name)

    for conn in current_device.connections:
        if conn.name not in visited:
            total_paths += count_paths(conn, visited.copy())

    return total_paths

total_paths = count_paths(start_device, set())
print(f"Total distinct paths from 'you' to 'out': {total_paths}")