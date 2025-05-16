#!/bin/bash

# Check if tag is provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 <tag_name>"
  exit 1
fi

TAG=$1

# Check if the tag exists
if ! git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Error: Tag '$TAG' does not exist"
  exit 1
fi

# Create a temporary directory to checkout the tag
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Get the Python script name
PYTHON_SCRIPT="dom-67386.py"

# Checkout the file at the specified tag
git show "$TAG:$PYTHON_SCRIPT" > "$TEMP_DIR/$PYTHON_SCRIPT"

# Make the script executable
chmod +x "$TEMP_DIR/$PYTHON_SCRIPT"

# Run the Python script
python "$TEMP_DIR/$PYTHON_SCRIPT"