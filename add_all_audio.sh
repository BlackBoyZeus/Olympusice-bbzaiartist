#!/bin/bash

# Find all song directories
find . -maxdepth 1 -type d -name "*\[*\]*" | while read -r dir; do
  # Check if audio directory exists
  if [ -d "$dir/audio" ]; then
    echo "Processing $dir..."
    # Add all WAV files
    find "$dir/audio" -type f -name "*.wav" -print0 | xargs -0 git add
    # Commit changes
    git commit -m "Add audio files from $dir"
    # Push to GitHub
    git push origin main
  fi
done
