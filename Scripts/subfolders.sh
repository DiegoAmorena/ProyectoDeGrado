#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <source_directory> <prefix> <number>"
    exit 1
fi

# Assign arguments to variables
SOURCE_DIR=$1
PREFIX=$2
NUMBER=$3

# Define the target directories
TARGET_DIRS=("medium" "small" "tiny" "base" "large")

# Create target directories if they don't exist
for DIR in "${TARGET_DIRS[@]}"; do
    mkdir -p "$SOURCE_DIR/$DIR"
done

# Move files to their corresponding directories
for FILE in "$SOURCE_DIR"/${PREFIX}_${NUMBER}_*; do
    if [[ -f "$FILE" ]]; then
        # Extract the base name of the file
        BASENAME=$(basename "$FILE")
        
        # Determine the target directory based on the file name
        case "$BASENAME" in
            *base*) TARGET_DIR="base" ;;
            *small*) TARGET_DIR="small" ;;
            *medium*) TARGET_DIR="medium" ;;
            *tiny*) TARGET_DIR="tiny" ;;
            *large*) TARGET_DIR="large" ;;
            *) TARGET_DIR="unknown" ;;
        esac
        
        # Move the file to the target directory
        mv "$FILE" "$SOURCE_DIR/$TARGET_DIR/"
    fi
done

echo "Files have been moved."
