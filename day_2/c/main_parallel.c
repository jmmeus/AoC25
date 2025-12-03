#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <stdatomic.h>

#define MAX_CHUNKS 10000 // Sufficient for our input size

typedef struct {
    long start;
    long end;
} Chunk;

// Shared State
Chunk chunks[MAX_CHUNKS];
int total_chunks = 0;
atomic_size_t current_chunk_index = 0;

// Optimized integer to string (base 10)
// Returns length
int fast_ultoa(unsigned long value, char* buffer) {
    char temp[24];
    char* p = temp;
    int len = 0;
    
    do {
        *p++ = (char)((value % 10) + '0');
        value /= 10;
        len++;
    } while (value > 0);
    
    // Reverse into buffer
    for (int i = 0; i < len; i++) {
        buffer[i] = *--p;
    }
    buffer[len] = '\0';
    return len;
}

// Worker function
void* process_queue(void* arg) {
    long long local_invalid_count = 0;
    char buffer[64];
    
    while (1) {
        // Atomic work stealing
        size_t my_index = atomic_fetch_add(&current_chunk_index, 1);
        if (my_index >= total_chunks) {
            break;
        }

        Chunk ch = chunks[my_index];
        
        for (long number = ch.start; number <= ch.end; number++) {
            // Convert number to string
            int len = fast_ultoa((unsigned long)number, buffer);
            
            if (len % 2 != 0) {
                continue;
            }
            
            int half = len / 2;
            if (strncmp(buffer, buffer + half, half) == 0) {
                local_invalid_count += number;
            }
        }
    }
    
    // Return result as pointer (cast needed)
    return (void*)local_invalid_count;
}

void add_chunks(long start, long end, int num_workers) {
    long total = end - start + 1;
    // Python logic: chunk_size = max(1, total // num_workers)
    // Note: Python's num_workers passed to split_range was (cpu_count * 4)
    long chunk_size = total / num_workers;
    if (chunk_size < 1) chunk_size = 1;

    long current = start;
    while (current <= end) {
        if (total_chunks >= MAX_CHUNKS) {
            fprintf(stderr, "Error: Exceeded MAX_CHUNKS\n");
            exit(1);
        }
        long chunk_end = current + chunk_size - 1;
        if (chunk_end > end) chunk_end = end;
        
        chunks[total_chunks].start = current;
        chunks[total_chunks].end = chunk_end;
        total_chunks++;
        
        current = chunk_end + 1;
    }
}

int main() {
    FILE *file = fopen("../input.txt", "r");
    if (!file) {
        // Fallback if running from c/ directory
        file = fopen("input.txt", "r");
        if (!file) {
            perror("Error opening file");
            return 1;
        }
    }

    char line[65536]; 
    if (!fgets(line, sizeof(line), file)) {
        fclose(file);
        return 1;
    }
    fclose(file);
    line[strcspn(line, "\r\n")] = 0;

    // 1. Setup Parallelism parameters
    int num_procs = sysconf(_SC_NPROCESSORS_ONLN);
    // Matches Python's multiplier for chunk granularity
    int target_chunks_per_range = num_procs * 4; 

    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    // 2. Parse and Chunk
    char *id_range = strtok(line, ",");
    while (id_range != NULL) {
        char *dash = strchr(id_range, '-');
        if (dash) {
            *dash = '\0';
            long start = atol(id_range);
            long end = atol(dash + 1);
            add_chunks(start, end, target_chunks_per_range);
        }
        id_range = strtok(NULL, ",");
    }

    // 3. Spawn Threads
    pthread_t threads[num_procs];
    for (int i = 0; i < num_procs; i++) {
        if (pthread_create(&threads[i], NULL, process_queue, NULL) != 0) {
            perror("Failed to create thread");
            return 1;
        }
    }

    // 4. Join and Accumulate
    long long final_total = 0;
    for (int i = 0; i < num_procs; i++) {
        void*retval;
        pthread_join(threads[i], &retval);
        final_total += (long long)retval;
    }

    clock_gettime(CLOCK_MONOTONIC, &end_time);
    double time_taken = (end_time.tv_sec - start_time.tv_sec) +
                        (end_time.tv_nsec - start_time.tv_nsec) / 1e9;

    printf("Parallel Execution time: %.6f seconds\n", time_taken);
    printf("Total invalid ID count: %lld\n", final_total);

    return 0;
}
