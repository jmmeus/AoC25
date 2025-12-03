# Read input from file
file = open("./input.txt", "r")

# We now need to generalise this for an arbitrary number of 'tens' or 'ones' positions
# e.g. if we have just tens and ones, we have 2 positions
# if we have hundreds, tens and ones, we have 3 positions, etc.

n = 12
total_joltage = 0
for line in file.readlines():
    bank = line.rstrip()

    # Let's say we have n positions
    max_digits = [-1] * n  # Initialize a list to store the max digits for each position

    # We need to process n numbers at a time
    for i in range(len(bank) - n + 1):
        candidates = [int(bank[i + j]) for j in range(n)]

        # Update max_digits list
        for j in range(n):
            if candidates[j] > max_digits[j]:
                max_digits[j] = candidates[j]
                # Reset all subsequent positions
                for k in range(j + 1, n):
                    max_digits[k] = candidates[k]
                break
            elif candidates[j] > max_digits[j]:
                max_digits[j] = candidates[j]
        
    # Calculate the total value for this bank
    bank_value = sum(max_digits[j] * (10 ** (n - j - 1)) for j in range(n))
    total_joltage += bank_value

print(f"Total joltage with {n} positions: {total_joltage}")