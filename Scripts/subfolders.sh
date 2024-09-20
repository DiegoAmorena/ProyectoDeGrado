#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <source_directory>"
    exit 1
fi

# Assign the argument to a variable
SOURCE_DIR=$1

# Define the target directories
TARGET_DIRS=("medium" "small" "tiny" "base" "large")

# Create target directories if they don't exist
for DIR in "${TARGET_DIRS[@]}"; do
    mkdir -p "$SOURCE_DIR/$DIR"
done

# Move files to their corresponding directories
for TARGET in "${TARGET_DIRS[@]}"; do
    # Find files that end with the target keyword and move them
    for FILE in "$SOURCE_DIR"/*$TARGET; do
        if [[ -f "$FILE" ]]; then
            # Move the file to the target directory
            mv "$FILE" "$SOURCE_DIR/$TARGET/"
        fi
    done
done

echo "Files have been moved."
