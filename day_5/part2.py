from time import perf_counter

# Read input from file
file = open("./input.txt", "r")

class SortedRanges:
    def __init__(self):
        self.ranges: list[tuple[int, int]] = []
    
    def insert(self, start: int, end: int):
        # Binary search to find the correct position to insert
        lo, hi = 0, len(self.ranges)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.ranges[mid][0] < start:
                lo = mid + 1
            else:
                hi = mid
        
        # Insert at the found position
        self.ranges.insert(lo, (start, end))

sorted_ranges = SortedRanges()
_raw_ranges: list[tuple[int, int]] = []

for line in file:
    if '-' in line:
        start, end = map(int, line.rstrip().split("-"))
        sorted_ranges.insert(start, end)
        _raw_ranges.append((start, end))
    else:
        break

# Now we have all ranges sorted, let's merge them
merged_ranges: list[tuple[int, int]] = []
for start, end in sorted_ranges.ranges:
    if not merged_ranges:
        merged_ranges.append((start, end))
    else:
        last_start, last_end = merged_ranges[-1]
        if start <= last_end + 1:  # Overlapping or contiguous ranges
            merged_ranges[-1] = (last_start, max(last_end, end))
        else:
            merged_ranges.append((start, end))


start_time_merged = perf_counter()

# As ranges are merged, we can trivially add the size of each merged range
# to find the total number of potentially valid ingredient IDs
valid_ingredient_ids: int = 0
for start, end in merged_ranges:
    valid_ingredient_ids += (end - start + 1)

end_time_merged = perf_counter()
print(f"Merged ranges check took {end_time_merged - start_time_merged:.6f} seconds")

# start_time_raw = perf_counter()

# For unsorted ranges, this is less trivial as there will be overlaps
# use a set to track unique valid ingredient IDs? Killer for memory and time lol
# _debug_unique_fresh_ingredient_ids: set[int] = set()
# for i, (start, end) in enumerate(_raw_ranges):
#     for ingredient_id in range(start, end + 1):
#         _debug_unique_fresh_ingredient_ids.add(ingredient_id)

# _debug_valid_ingredient_ids: int = len(_debug_unique_fresh_ingredient_ids)
    
# end_time_raw = perf_counter()
# print(f"Raw ranges check took {end_time_raw - start_time_raw:.6f} seconds")

print(f"Number of valid fresh ingredients ids: {valid_ingredient_ids}")