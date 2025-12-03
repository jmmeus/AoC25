# Day 2: Gift Shop

This directory contains solutions for Day 2 of Advent of Code 2025, including a performance comparison between Python, C, and Rust implementations (both serial and parallel).

## Implementation Details

*   **Serial Code:** The serial implementations in Python (`part1.py`, `part2.py`), C (`c/main.c`), and Rust (`rust/src/main.rs`) were written manually.
*   **Parallel Python:** The parallel Python implementation (`part1_parallel.py`) was also written manually.
*   **Parallel C & Rust:** The parallel implementations for C (`c/main_parallel.c`) and Rust (`rust/src/bin/parallel.rs`) were developed with the assistance of generative AI models (**Gemini Pro 3** and **Claude Sonnet 4.5**) to explore performance optimizations and concurrency patterns in these languages. Notably, it was fun to discover that the custom conversion logic in the two parallel scripts improved both the lock condition of C's `sprintf` as well as Rust's heap allocation.

## Benchmarks

A benchmarking suite (`benchmark_suite.py`) was used to compare the performance of the different implementations. The results highlight the significant speedups achieved through compilation and parallelization.

| Language        | Avg Time   | Speedup    |
| :-------------- | :--------- | :--------- |
| Rust (Par)      | 0.002387   | 332.72x    |
| C (Par)         | 0.002785   | 285.20x    |
| Rust            | 0.074381   | 10.68x     |
| C               | 0.081482   | 9.75x      |
| Python (Par)    | 0.121374   | 6.54x      |
| Python          | 0.794371   | 1.00x      |
