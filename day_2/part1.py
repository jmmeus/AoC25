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
        if len(str(number)) % 2 != 0:
            continue
        first_half, second_half = str(number)[:len(str(number))//2], str(number)[len(str(number))//2:]
        if first_half == second_half:
            total_invalid += number

end_time = perf_counter()
print(f"Execution time: {end_time - start_time:.6f} seconds")

print(f"Total invalid ID count: {total_invalid}")