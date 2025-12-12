from __future__ import annotations

# Read input from file
file = open("./input.txt", "r")

# Build the directed graph
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

print(f"Graph loaded: {len(devices)} devices")
print("=" * 60)

# Three-colour DFS cycle detection
# WHITE (0): Not visited yet
# GRAY (1): Currently being visited (in DFS stack)
# BLACK (2): Completely explored

WHITE = 0
GRAY = 1
BLACK = 2

colors: dict[str, int] = {name: WHITE for name in devices.keys()}
cycles_found: list[list[str]] = []
current_path: list[str] = []


def dfs(node_name: str) -> bool:
    """
    Performs DFS with three-colour marking.
    Returns True if a cycle is detected, False otherwise.
    """
    colors[node_name] = GRAY
    current_path.append(node_name)

    device = devices[node_name]

    for conn in device.connections:
        if colors[conn.name] == GRAY:
            # Back edge detected - we found a cycle!
            # Extract the cycle from current_path
            cycle_start_idx = current_path.index(conn.name)
            cycle = current_path[cycle_start_idx:] + [conn.name]
            cycles_found.append(cycle)
            return True

        if colors[conn.name] == WHITE:
            if dfs(conn.name):
                return True

    colors[node_name] = BLACK
    current_path.pop()
    return False


# Check for cycles starting from each unvisited node
has_cycle = False
for device_name in devices.keys():
    if colors[device_name] == WHITE:
        if dfs(device_name):
            has_cycle = True
            # Continue to find more cycles (optional - we could break here)

print(f"Is the graph a DAG? {not has_cycle}")
print("=" * 60)

if has_cycle:
    print(f"\nCYCLES DETECTED! Found {len(cycles_found)} cycle(s):")
    print("=" * 60)

    # Show up to 10 example cycles
    for i, cycle in enumerate(cycles_found[:10]):
        print(f"\nCycle {i + 1}:")
        print("  " + " -> ".join(cycle))

    if len(cycles_found) > 10:
        print(f"\n... and {len(cycles_found) - 10} more cycles")

    print("\n" + "=" * 60)
    print("CONCLUSION: The graph is NOT a DAG (contains cycles)")
    print("=" * 60)
else:
    print("\nNo cycles detected!")
    print("=" * 60)
    print("CONCLUSION: The graph IS a DAG (Directed Acyclic Graph)")
    print("=" * 60)
