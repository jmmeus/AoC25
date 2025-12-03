use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;
use std::time::Instant;
use std::thread;
use std::sync::{Arc, atomic::{AtomicUsize, Ordering}};

struct Chunk {
    start: i64,
    end: i64,
}

fn main() -> io::Result<()> {
    // 1. Read File
    let path = Path::new("../input.txt");
    let file = File::open(&path).or_else(|_| File::open("input.txt"))?;
    let mut reader = io::BufReader::new(file);
    let mut line = String::new();
    reader.read_line(&mut line)?;
    let line = line.trim();

    // 2. Determine Parallelism
    let num_threads = thread::available_parallelism().map(|n| n.get()).unwrap_or(1);
    // Match Python/C granularity logic
    let chunks_split_factor = num_threads * 4; 

    let start_time = Instant::now();

    // 3. Generate Chunks
    let mut chunks = Vec::new();
    for id_range in line.split(',') {
        let parts: Vec<&str> = id_range.split('-').collect();
        if parts.len() != 2 { continue; }
        
        let start: i64 = parts[0].parse().unwrap();
        let end: i64 = parts[1].parse().unwrap();
        
        let total = end - start + 1;
        let chunk_size = std::cmp::max(1, total / chunks_split_factor as i64);
        
        let mut current = start;
        while current <= end {
            let chunk_end = std::cmp::min(current + chunk_size - 1, end);
            chunks.push(Chunk { start: current, end: chunk_end });
            current = chunk_end + 1;
        }
    }

    // 4. Shared State
    let chunks_arc = Arc::new(chunks);
    let counter = Arc::new(AtomicUsize::new(0));
    let mut handles = vec![];

    // 5. Spawn Workers
    for _ in 0..num_threads {
        let chunks_ref = Arc::clone(&chunks_arc);
        let counter_ref = Arc::clone(&counter);
        
        let handle = thread::spawn(move || {
            let mut local_sum: i64 = 0;
            let num_chunks = chunks_ref.len();
            // Buffer for integer to string conversion (max i64 is 19 digits + sign)
            let mut buffer = [0u8; 20];

            loop {
                // Atomic work stealing
                let idx = counter_ref.fetch_add(1, Ordering::Relaxed);
                if idx >= num_chunks {
                    break;
                }

                let chunk = &chunks_ref[idx];
                for number in chunk.start..=chunk.end {
                    // Custom fast itoa implementation (no allocation)
                    let mut n = number;
                    let len;
                    
                    // Handle 0 explicitly (though input is positive, good practice)
                    if n == 0 {
                        buffer[0] = b'0';
                        len = 1;
                    } else {
                        let mut p = 0;
                        while n > 0 {
                            buffer[p] = (n % 10) as u8 + b'0';
                            n /= 10;
                            p += 1;
                        }
                        len = p;
                        // Buffer now contains the digits in reverse order
                    }

                    if len % 2 != 0 { continue; }
                    
                    let half = len / 2;
                    // Check if first half equals second half
                    // Since the string is reversed in the buffer, 
                    // we are technically comparing the reversed second half with the reversed first half.
                    // "123123" -> reversed is "321321".
                    // First half "321", Second half "321". They match!
                    // So, we don't need to reverse the buffer to check equality of halves

                    let (first, second) = buffer[..len].split_at(half);
                    if first == second {
                        local_sum += number;
                    }
                }
            }
            local_sum
        });
        handles.push(handle);
    }

    // 6. Join and Reduce
    let mut total_invalid = 0;
    for handle in handles {
        total_invalid += handle.join().unwrap();
    }

    let duration = start_time.elapsed();
    println!("Parallel Execution time: {:.6} seconds", duration.as_secs_f64());
    println!("Total invalid ID count: {}", total_invalid);

    Ok(())
}
