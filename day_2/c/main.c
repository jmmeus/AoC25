#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main() {
    FILE *file = fopen("../input.txt", "r");
    if (!file) {
        perror("Error opening file");
        return 1;
    }

    char line[65536]; // Assuming the line fits in buffer
    if (!fgets(line, sizeof(line), file)) {
        fclose(file);
        return 1;
    }
    fclose(file);

    // Remove trailing newline if present
    line[strcspn(line, "\r\n")] = 0;

    long long total_invalid = 0;
    char buffer[64]; // Buffer for number string conversion

    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    char *id_range = strtok(line, ",");
    while (id_range != NULL) {
        long start, end;
        char *dash = strchr(id_range, '-');
        if (dash) {
            *dash = '\0';
            start = atol(id_range);
            end = atol(dash + 1);
            
            for (long number = start; number <= end; number++) {
                // Convert number to string
                int len = sprintf(buffer, "%ld", number);
                
                if (len % 2 != 0) {
                    continue;
                }
                
                int half = len / 2;
                // Compare first half and second half
                // first half is buffer[0]...buffer[half-1]
                // second half is buffer[half]...buffer[len-1]
                
                if (strncmp(buffer, buffer + half, half) == 0) {
                    total_invalid += number;
                }
            }
        }
        id_range = strtok(NULL, ",");
    }

    clock_gettime(CLOCK_MONOTONIC, &end_time);
    double time_taken = (end_time.tv_sec - start_time.tv_sec) +
                        (end_time.tv_nsec - start_time.tv_nsec) / 1e9;

    printf("Execution time: %.6f seconds\n", time_taken);
    printf("Total invalid ID count: %lld\n", total_invalid);

    return 0;
}
