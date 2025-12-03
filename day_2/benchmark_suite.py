import subprocess
import re

def run_benchmark(name: str, command: str, iterations: int = 10) -> float | None:
    times: list[float] = []
    print(f"Benchmarking {name} ({iterations} runs)...")
    
    for i in range(iterations):
        # Run command using shell
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error running {name}: {result.stderr}")
            return None
            
        # Extract time
        # Matches:
        # "Execution time: 0.123 seconds" (Serial)
        # "Parallel Execution time: 0.123 seconds" (Parallel)
        match = re.search(r"(?:Execution time|Parallel Execution time): (\d+\.\d+)", result.stdout)
        if match:
            duration = float(match.group(1))
            times.append(duration)
        else:
            print(f"  Run {i+1}: Could not parse time from output: {result.stdout.strip()[:50]}...")

    if times:
        avg_time = sum(times) / len(times)
        print(f"{name} Average: {avg_time:.6f} seconds")
        return avg_time
    return None

print("-" * 45)

# List of benchmarks to run
# Tuples of (Display Name, Shell Command)
benchmarks = [
    ("Python", "cd .. && python3 day_2/part1.py"),
    ("Python (Par)", "python3 part1_parallel.py"),
    ("C", "cd c && ./main"),
    ("C (Par)", "cd c && ./main_parallel"),
    ("Rust", "cd rust && ./target/release/rust"),
    ("Rust (Par)", "cd rust && ./target/release/parallel")
]

raw_results: list[tuple[str, float]] = []
for name, cmd in benchmarks:
    avg = run_benchmark(name, cmd)
    if avg is not None:
        raw_results.append((name, avg))

print("-" * 45)
print(f"| {'Language':<15} | {'Avg Time':<10} | {'Speedup':<10} |")
print("-" * 45)

# Sort results by Average Time (ascending - fastest first)
results = sorted(raw_results, key=lambda x: x[1])

# Determine baseline for speedup calculation
# Prefer "Python" (Serial) as baseline (1.0x).
# If not present, use the slowest execution time as fallback baseline.
python_entry = next((x for x in results if x[0] == "Python"), None)
if python_entry:
    baseline_time = python_entry[1]
else:
    # Fallback to slowest if Python serial failed or missing
    baseline_time = results[-1][1] if results else 1.0

for name, avg in results:
    speedup = baseline_time / avg if avg > 0 else 0.0
    print(f"| {name:<15} | {avg:<10.6f} | {f'{speedup:.2f}x':<10} |")

print("-" * 45)
