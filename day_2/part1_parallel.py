from time import perf_counter
from multiprocessing import Pool, cpu_count

def process_chunk(args: tuple[int, int]) -> int:
    start, end = args
    invalid_count = 0
    for number in range(start, end + 1):
        s = str(number)
        if len(s) % 2 != 0:
            continue
        mid = len(s) // 2
        if s[:mid] == s[mid:]:
            invalid_count += number
    return invalid_count

def split_range(id_range: str, num_chunks: int) -> list[tuple[int, int]]:
    """Split a range into num_chunks smaller ranges"""
    start, end = map(int, id_range.split("-"))
    total = end - start + 1
    chunk_size = max(1, total // num_chunks)
    
    chunks: list[tuple[int, int]] = []
    current = start
    while current <= end:
        chunk_end = min(current + chunk_size - 1, end)
        chunks.append((current, chunk_end))
        current = chunk_end + 1
    return chunks

if __name__ == "__main__":
    file = open("./input.txt", "r")
    line = file.readline().strip()

    # Fine-grained approach // split all ranges into smaller chunks
    num_workers = cpu_count() * 4  # Adjust multiplier as needed ?
    start_time_fine = perf_counter()
    all_chunks: list[tuple[int, int]] = []
    for id_range in line.split(","):
        all_chunks.extend(split_range(id_range, num_workers))
    
    
    with Pool() as pool:
        results = pool.map(process_chunk, all_chunks)
    total_fine = sum(results)
    end_time_fine = perf_counter()
    print(f"Parallel Execution time: {end_time_fine - start_time_fine:.6f} seconds")
    print(f"Total invalid ID count: {total_fine}")