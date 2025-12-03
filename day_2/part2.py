from time import perf_counter

# Read input from file
file = open("day_2/input.txt", "r")

total_invalid = 0

line = file.readline().strip()

start_time = perf_counter()

for id_range in line.split(","):
    assert "-" in id_range
    start, end = map(int, id_range.split("-"))
    for number in range(start, end + 1):
        for split_count in range(2, len(str(number)) + 1):
            if len(str(number)) % split_count != 0:
                continue
            segment_length = len(str(number)) // split_count
            segments = [str(number)[i*segment_length:(i+1)*segment_length] for i in range(split_count)]
            if all(segment == segments[0] for segment in segments[1:]):
                total_invalid += number
                break

end_time = perf_counter()
print(f"Execution time: {end_time - start_time:.6f} seconds")

print(f"Total invalid ID count: {total_invalid}")