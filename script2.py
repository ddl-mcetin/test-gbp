#!/usr/bin/env python3
import time
import random
from datetime import datetime
import os # Added import

# Wait for 5 seconds
time.sleep(5)

# Generate 5 random numbers
random_numbers = [random.randint(1, 100) for _ in range(5)]

# Get current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Prepare output with timestamp
output = f"{timestamp}: {', '.join(map(str, random_numbers))}\n"

# Define the results directory path
# Standard path for Domino job results
results_dir = "/mnt/artifacts/results"

# Create the results directory if it doesn't exist
# Domino usually creates this, but it's good practice to ensure it exists.
os.makedirs(results_dir, exist_ok=True)

# Construct the full path for the output file
output_file_path = os.path.join(results_dir, "output2.txt")

# Append to output.txt in the results directory
with open(output_file_path, "a") as file:
    file.write(output)

print(f"Added random numbers to {output_file_path}: {', '.join(map(str, random_numbers))}")
