# Day 4: Printing Department

This directory contains solutions for Day 4 of Advent of Code 2025, including a performance comparison between three different algorithmic and optimization approaches in Python.

## Problem Overview

The problem involves simulating a cascade effect on a grid of paper pieces (`@` characters). Papers with fewer than 4 adjacent neighbors are removed, which may cause neighboring papers to then have fewer than 4 neighbors, triggering a cascade of removals.

## Implementation Details

### 1. Original (Iterative) - `part2.py`
The baseline implementation uses a multi-pass iterative approach:
- Repeatedly scans the entire grid until no more changes occur
- Uses a sliding 3-line window for memory efficiency
- Stores changes in a set and applies them on subsequent iterations
- **Complexity:** O(n² × k) where n is grid size and k is cascade depth

### 2. Two-Pass Queue - `part2_optimised.py`
An algorithmic optimization using a queue-based cascade:
- **Pass 1:** Parse grid and identify all paper positions
- **Pass 2:** Calculate neighbor counts and queue immediately removable papers
- **BFS Processing:** When removing a paper, decrement neighbor counts and queue newly removable neighbors
- Custom `Queue` class implemented to avoid external dependencies
- **Complexity:** O(n) - each cell visited constant times
- **Key Insight:** When a cell is removed, only its 8 neighbors are affected, eliminating redundant scans

### 3. Two-Pass + ByteGrid - `part2_bytegrid.py`
Combines algorithmic optimization with memory optimization:
- Same two-pass queue algorithm as above
- Uses flat `bytearray` instead of nested lists
- **Bit packing:** Each byte stores both paper state and neighbor count
  - Bit 7 (0x80): Paper present flag
  - Bits 0-3 (0x0F): Neighbor count (0-8)
- Better memory locality with contiguous flat array
- **Trade-off:** In Python, bit manipulation overhead offsets some speed benefits

## Benchmarks

A benchmarking suite (`benchmark.py`) was used to compare the performance of the different implementations. The suite can run in either TIME or MEMORY mode using the `BENCHMARK` environment variable.

### Time Benchmark (10 runs average)

```
===========================================================
| Implementation            | Avg Time     | Speedup      |
===========================================================
| Two-Pass Queue            | 0.028021     | 9.81x        |
| Two-Pass + ByteGrid       | 0.036784     | 7.47x        |
| Original (Iterative)      | 0.274754     | 1.00x        |
===========================================================
```

### Memory Benchmark (10 runs average)

```
============================================================
| Implementation            | Avg Memory   | Reduction     |
============================================================
| Two-Pass + ByteGrid       | 0.11 MB      | 9.18x (89.1%) |
| Two-Pass Queue            | 0.34 MB      | 2.97x (66.3%) |
| Original (Iterative)      | 1.01 MB      | 1.00x ( 0.0%) |
============================================================
```

## Key Findings

### Speed Champion: Two-Pass Queue (9.81x speedup)
- The algorithmic improvement from O(n² × k) to O(n) provides massive gains
- Python's native list operations are highly optimized
- Achieves best execution time while maintaining reasonable memory usage

### Memory Champion: Two-Pass + ByteGrid (89.1% reduction)
- Uses only 0.11 MB compared to 1.01 MB for the original
- Line-by-line file reading eliminates string storage overhead (~30 KB)
- Flat byte array with bit packing dramatically reduces memory footprint
- Slightly slower than two-pass queue (7.47x vs 9.81x) due to Python's bit manipulation overhead
- **Note:** In lower-level languages (C/Rust), bytegrid would likely be fastest due to better cache locality and cheaper bit operations. Maybe I'll implement these if time allows.
