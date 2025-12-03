use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;
use std::time::Instant;

fn main() -> io::Result<()> {
    // Attempt to open the file. Assuming running from day_2/rust/
    let path = Path::new("../input.txt");
    let file = File::open(&path)?;
    let mut reader = io::BufReader::new(file);

    let mut line = String::new();
    reader.read_line(&mut line)?;
    let line = line.trim();

    let mut total_invalid = 0;

    let start_time = Instant::now();

    for id_range in line.split(',') {
        let parts: Vec<&str> = id_range.split('-').collect();
        if parts.len() != 2 {
            continue;
        }
        let start: i64 = parts[0].parse().unwrap();
        let end: i64 = parts[1].parse().unwrap();

        for number in start..=end {
            let s = number.to_string();
            let len = s.len();
            if len % 2 != 0 {
                continue;
            }
            let half = len / 2;
            let first_half = &s[..half];
            let second_half = &s[half..];

            if first_half == second_half {
                total_invalid += number;
            }
        }
    }

    let duration = start_time.elapsed();
    println!("Execution time: {:.6} seconds", duration.as_secs_f64());
    println!("Total invalid ID count: {}", total_invalid);

    Ok(())
}