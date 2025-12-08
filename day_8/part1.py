from __future__ import annotations

# Read input from file
file = open("./input.txt", "r")

# Define a simple 3D vector class
class Vector3D:
    x: int
    y: int
    z: int

    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def cartesian_distance(self, other: Vector3D) -> float:
        return (self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2

# Let's read in all coordinates
coordinates: list[Vector3D] = []
for line in file:
    line = line.rstrip()
    parts = line.split(',')
    coord = Vector3D(int(parts[0]), int(parts[1]), int(parts[2]))
    coordinates.append(coord)

# Now time to find all cartedian distances and keep them sorted
# from smallest to largest, note that the squared distance is all
# we need for relative comparisons
distances: list[tuple[float, tuple[Vector3D, Vector3D]]] = []
for i in range(len(coordinates)):
    for j in range(i + 1, len(coordinates)):
        dist = coordinates[i].cartesian_distance(coordinates[j])
        distances.append((dist, (coordinates[i], coordinates[j])))

sorted_distances = sorted(distances)

# Now process first N shortest distances, and create 'linked' clusters
n = 1000
clusters: list[set[Vector3D]] = []
for dist, (point_a, point_b) in sorted_distances:
    if n == 0:
        break
    # Check if either point is already in a cluster
    # We need to merge clusters if both points are in different clusters
    cluster_a = None
    cluster_b = None
    for cluster in clusters:
        if point_a in cluster:
            cluster_a = cluster
        if point_b in cluster:
            cluster_b = cluster
    if cluster_a and cluster_b:
        if cluster_a != cluster_b:
            # Merge clusters
            cluster_a.update(cluster_b)
            clusters.remove(cluster_b)
    elif cluster_a:
        cluster_a.add(point_b)
    elif cluster_b:
        cluster_b.add(point_a)
    else:
        # Create new cluster
        new_cluster: set[Vector3D] = set()
        new_cluster.add(point_a)
        new_cluster.add(point_b)
        clusters.append(new_cluster)
    n -= 1

# Multiple length of top M largest clusters
m = 3
clusters.sort(key=lambda c: len(c), reverse=True)
result = 1
for i in range(min(m, len(clusters))):
    result *= len(clusters[i])

print(f"Product of sizes of top {m} largest clusters: {result}")

# We might be able to optimise this using a kd-tree structure for
# nearest-neighbour searching, but for now this brute-force approach
# should be sufficient for the input size. Might be a fun exercise
# to implement later.