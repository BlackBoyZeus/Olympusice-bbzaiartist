#!/bin/bash

# Add all Python files
echo "Adding Python files..."
find . -name "*.py" -not -path "*/venv/*" -not -path "*/ai_music_env/*" -not -path "*/myenv/*" -print0 | xargs -0 git add

# Add all JSON files
echo "Adding JSON files..."
find . -name "*.json" -not -path "*/venv/*" -not -path "*/ai_music_env/*" -not -path "*/myenv/*" -print0 | xargs -0 git add

# Add all text files
echo "Adding text files..."
find . -name "*.txt" -not -path "*/venv/*" -not -path "*/ai_music_env/*" -not -path "*/myenv/*" -print0 | xargs -0 git add

# Add all MIDI files
echo "Adding MIDI files..."
find . -name "*.mid" -not -path "*/venv/*" -not -path "*/ai_music_env/*" -not -path "*/myenv/*" -print0 | xargs -0 git add

# Add all PNG files
echo "Adding PNG files..."
find . -name "*.png" -not -path "*/venv/*" -not -path "*/ai_music_env/*" -not -path "*/myenv/*" -print0 | xargs -0 git add

# Add all NPY files
echo "Adding NPY files..."
find . -name "*.npy" -not -path "*/venv/*" -not -path "*/ai_music_env/*" -not -path "*/myenv/*" -print0 | xargs -0 git add

# Commit non-audio files
git commit -m "Add all non-audio files"
git push origin main

# Process audio files in batches
echo "Processing audio files in batches..."
find . -name "*.wav" -not -path "*/venv/*" -not -path "*/ai_music_env/*" -not -path "*/myenv/*" | sort > all_audio_files.txt
total_files=$(wc -l < all_audio_files.txt)
batch_size=10
current=0

while [ $current -lt $total_files ]; do
  echo "Processing batch $((current/batch_size + 1))..."
  head -n $batch_size all_audio_files.txt | tail -n $batch_size | while read -r file; do
    git add "$file"
  done
  git commit -m "Add audio files batch $((current/batch_size + 1))"
  git push origin main
  current=$((current + batch_size))
  sed -i '' "1,$batch_size d" all_audio_files.txt
done

echo "All files added to repository!"
