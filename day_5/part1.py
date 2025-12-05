from time import perf_counter

# Read input from file
file = open("./input.txt", "r")

# A simple approach would be to just store all the ranges, but that's boring
# Instead, let's sort the ranges by their starting point and then merge them 
# to get a unique set of ranges

# ============= RUN 1: Without sorted ranges (raw) =============
start_time_raw = perf_counter()

raw_ranges: list[tuple[int, int]] = []
raw_ingredient_ids: list[int] = []

for line in file:
    if '-' in line:
        start, end = map(int, line.rstrip().split("-"))
        raw_ranges.append((start, end))
    elif line.rstrip():
        num = int(line.rstrip())
        raw_ingredient_ids.append(num)

fresh_ingredients_raw: int = 0
for ingredient_id in raw_ingredient_ids:
    found = False
    for start, end in raw_ranges:
        if start <= ingredient_id <= end:
            found = True
            break
    if found:
        fresh_ingredients_raw += 1

end_time_raw = perf_counter()

# ============= RUN 2: With sorted and merged ranges =============
file.seek(0)  # Reset file to beginning

# We'll create a class to manage the sorted ranges
# with a simple insert method to prevent external deps
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

start_time_merged = perf_counter()

sorted_ranges = SortedRanges()
ingredient_ids: list[int] = []

for line in file:
    if '-' in line:
        start, end = map(int, line.rstrip().split("-"))
        sorted_ranges.insert(start, end)
    elif line.rstrip():
        num = int(line.rstrip())
        ingredient_ids.append(num)

# Merge the sorted ranges
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

fresh_ingredients_merged: int = 0
for ingredient_id in ingredient_ids:
    found = False
    for start, end in merged_ranges:
        if start <= ingredient_id <= end:
            found = True
            break
    if found:
        fresh_ingredients_merged += 1

end_time_merged = perf_counter()

# ============= RESULTS =============
print(f"Raw ranges check took {end_time_raw - start_time_raw:.6f} seconds")
print(f"Merged ranges check took {end_time_merged - start_time_merged:.6f} seconds")
print(f"Number of fresh ingredients (raw): {fresh_ingredients_raw}")
print(f"Number of fresh ingredients (merged): {fresh_ingredients_merged}")

file.close()