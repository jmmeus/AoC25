import subprocess
import re
import os
from typing import Literal

# Read benchmark type from environment (TIME or MEMORY)
BENCHMARK_TYPE: Literal["TIME", "MEMORY"] = os.environ.get("BENCHMARK", "TIME")  # type: ignore

def run_benchmark(name: str, script: str, benchmark_type: str, iterations: int = 10) -> tuple[float, str] | None:
    """
    Run a benchmark script multiple times and return average result.

    Returns: (average_value, output_result) or None if failed
    """
    values: list[float] = []
    result_line: str = ""

    print(f"Benchmarking {name} ({iterations} runs)...")

    for i in range(iterations):
        # Run script with BENCHMARK environment variable set
        result = subprocess.run(
            ["python3", script],
            capture_output=True,
            text=True,
            env={**os.environ, "BENCHMARK": benchmark_type}
        )

        if result.returncode != 0:
            print(f"  Error running {name}: {result.stderr}")
            return None

        # Extract timing or memory metric based on benchmark type
        if benchmark_type == "TIME":
            # Match patterns like:
            # "Iterative Execution time: 0.123456 seconds"
            # "Two-Pass Queue Execution time: 0.123456 seconds"
            # "ByteGrid Execution time: 0.123456 seconds"
            match = re.search(r"Execution time: (\d+\.\d+) seconds", result.stdout)
            if match:
                value = float(match.group(1))
                values.append(value)
            else:
                print(f"  Run {i+1}: Could not parse time from output")
        else:  # MEMORY
            # Match pattern like: "Peak memory usage: 12.34 MB"
            match = re.search(r"Peak memory usage: (\d+\.\d+) MB", result.stdout)
            if match:
                value = float(match.group(1))
                values.append(value)
            else:
                print(f"  Run {i+1}: Could not parse memory from output")

        # Extract result line (the line with "Total '@' characters...")
        if i == 0:  # Only need to capture once
            result_match = re.search(r"Total '@' characters.*: (\d+)", result.stdout)
            if result_match:
                result_line = result_match.group(1)

    if values:
        avg_value = sum(values) / len(values)
        print(f"  {name} Average: {avg_value:.6f} {'seconds' if benchmark_type == 'TIME' else 'MB'}")
        return (avg_value, result_line)

    return None

print("=" * 70)
print(f"Running benchmarks in {BENCHMARK_TYPE} mode")
print("=" * 70)

# List of benchmarks to run
# Tuples of (Display Name, Script Path)
benchmarks = [
    ("Original (Iterative)", "part2.py"),
    ("Two-Pass Queue", "part2_optimised.py"),
    ("Two-Pass + ByteGrid", "part2_bytegrid.py")
]

raw_results: list[tuple[str, float, str]] = []
results_set: set[str] = set()

for name, script in benchmarks:
    result = run_benchmark(name, script, BENCHMARK_TYPE)
    if result is not None:
        avg_value, result_line = result
        raw_results.append((name, avg_value, result_line))
        results_set.add(result_line)

print("=" * 70)

# Verify all results are identical
if len(results_set) == 1:
    print(f"✓ All implementations produce the same result: {results_set.pop()} papers removed")
elif len(results_set) > 1:
    print(f"✗ WARNING: Different results detected!")
    for name, _, result in raw_results:
        print(f"  {name}: {result}")
else:
    print("✗ No valid results obtained")

print("=" * 70)

# Sort results by value (ascending - best first)
# For TIME: lower is better; for MEMORY: lower is better
results = sorted(raw_results, key=lambda x: x[1])

# Use original (iterative) as baseline for speedup calculation
baseline_entry = next((x for x in results if "Original" in x[0]), None)
if baseline_entry:
    baseline_value = baseline_entry[1]
else:
    # Fallback to slowest/most memory intensive
    baseline_value = results[-1][1] if results else 1.0

# Print comparison table
metric = "Avg Time" if BENCHMARK_TYPE == "TIME" else "Avg Memory"
improvement_label = "Speedup" if BENCHMARK_TYPE == "TIME" else "Reduction"

print(f"| {'Implementation':<25} | {metric:<12} | {improvement_label:<12} |")
print("=" * 70)

for name, value, _ in results:
    # Calculate improvement factor
    if BENCHMARK_TYPE == "TIME":
        improvement = baseline_value / value if value > 0 else 0.0
        print(f"| {name:<25} | {value:<12.6f} | {f'{improvement:.2f}x':<12} |")
    else:  # MEMORY
        improvement = baseline_value / value if value > 0 else 0.0
        reduction_pct = (1 - value / baseline_value) * 100 if baseline_value > 0 else 0.0
        print(f"| {name:<25} | {value:<12.2f} | {f'{improvement:.2f}x ({reduction_pct:.1f}%)':<12} |")

print("=" * 70)
