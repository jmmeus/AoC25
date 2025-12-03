# Read input from file
file = open("./input.txt", "r")

total_joltage = 0
for line in file.readlines():
    bank = line.rstrip()
    # We're going to go through the bank number by number
    # We're going to store a 'tens' number and a 'ones' number
    # Each of these two numbers have to occur 'in the right order'
    # For tens, we go through all numbers except the last and for ones,
    # we go through all numbers except the first. We want to store the largest
    # of each (BUT we need to reset the ones number when we find a new tens number)
    # e.g. for bank "3675356291" we end up with tens=9 and ones=1, giving us 91
    tens = -1
    ones = -1
    for i in range(len(bank)-1):
        ten_candidate = int(bank[i])
        one_candidate = int(bank[i+1])
        if ten_candidate > tens:
            tens = ten_candidate
            ones = one_candidate  # Reset ones when we find a new tens
        elif one_candidate > ones:
            ones = one_candidate
    total_joltage += tens * 10 + ones

print(f"Total joltage: {total_joltage}")