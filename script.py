#!/usr/bin/env python3
import time
import random
from datetime import datetime

# Wait for 5 seconds
time.sleep(5)

# Generate 5 random numbers
random_numbers = [random.randint(1, 100) for _ in range(5)]

# Get current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Prepare output with timestamp
output = f"{timestamp}: {', '.join(map(str, random_numbers))}\n"

# Append to output.txt if it exists, otherwise create it
with open("output.txt", "a") as file:
    file.write(output)

print(f"Added random numbers to output.txt: {', '.join(map(str, random_numbers))}")