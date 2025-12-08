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
    
    def __repr__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

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

# Now we simply process all distances, and should end up with
# a single cluster at the end // track final 'merging' vectors
clusters: list[set[Vector3D]] = []
latest_pair: tuple[Vector3D, Vector3D] = (Vector3D(0,0,0), Vector3D(0,0,0))
for dist, (point_a, point_b) in sorted_distances:
    latest_pair = (point_a, point_b)
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

    if len(clusters) == 1 and len(clusters[0]) == len(coordinates):
        # Just len(clusters) == 1 would trigger on creation of first cluster
        # and just going through ALL distances would miss the actual vectors
        # of the final merge.
        break

print(f"Latest merged pair: {latest_pair[0]} - {latest_pair[1]}")
print(f"Number of clusters: {len(clusters)}")
x1_times_x2 = latest_pair[0].x * latest_pair[1].x
print(f"Product of x-coordinates: {x1_times_x2}")