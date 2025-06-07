#!/usr/bin/env python3
"""
Script to create a master dataset from all song directories.
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path
import numpy as np

def parse_arguments():
    parser = argparse.ArgumentParser(description="Create a master dataset from all song directories")
    parser.add_argument("--root-dir", type=str, default="/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)Main/music_generator",
                        help="Root directory containing song directories")
    parser.add_argument("--output-dir", type=str, default="/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)Main/music_generator/master_dataset",
                        help="Output directory for master dataset")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing files")
    return parser.parse_args()

def is_song_directory(path):
    """Check if a directory is a song directory."""
    # Check if it has audio, lyrics, or features.json
    return (os.path.isdir(os.path.join(path, "audio")) or
            os.path.isdir(os.path.join(path, "lyrics")) or
            os.path.exists(os.path.join(path, "features.json")))

def get_song_name(directory):
    """Extract song name from directory name."""
    # If directory name has a YouTube ID in brackets, extract the name
    if "[" in directory and "]" in directory:
        return directory.split("[")[0].strip()
    return directory

def get_song_id(directory):
    """Extract song ID from directory name."""
    # If directory name has a YouTube ID in brackets, extract the ID
    if "[" in directory and "]" in directory:
        return directory.split("[")[1].split("]")[0].strip()
    return ""

def process_song_directory(song_dir, output_dir, force=False):
    """Process a song directory and add it to the master dataset."""
    song_dir_path = Path(song_dir)
    song_dir_name = song_dir_path.name
    song_name = get_song_name(song_dir_name)
    song_id = get_song_id(song_dir_name)
    
    print(f"Processing {song_dir_name}...")
    
    # Create output directories
    features_dir = os.path.join(output_dir, "features")
    lyrics_dir = os.path.join(output_dir, "lyrics")
    metadata_dir = os.path.join(output_dir, "metadata")
    spectrograms_dir = os.path.join(output_dir, "spectrograms")
    
    os.makedirs(features_dir, exist_ok=True)
    os.makedirs(lyrics_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    os.makedirs(spectrograms_dir, exist_ok=True)
    
    # Initialize song data
    song_data = {
        "song_name": song_name,
        "song_id": song_id,
        "directory": str(song_dir_path),
        "has_audio": False,
        "has_lyrics": False,
        "has_features": False,
        "has_mel_spectrogram": False,
        "has_metadata": False
    }
    
    # Check for audio files
    audio_dir = song_dir_path / "audio"
    if audio_dir.exists() and audio_dir.is_dir():
        audio_files = list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav"))
        if audio_files:
            song_data["has_audio"] = True
            song_data["audio_file"] = str(audio_files[0].relative_to(song_dir_path))
    
    # Check for lyrics
    lyrics_dir_path = song_dir_path / "lyrics"
    if lyrics_dir_path.exists() and lyrics_dir_path.is_dir():
        lyrics_files = list(lyrics_dir_path.glob("*.txt"))
        if lyrics_files:
            song_data["has_lyrics"] = True
            lyrics_file = lyrics_files[0]
            song_data["lyrics_file"] = str(lyrics_file.relative_to(song_dir_path))
            
            # Copy lyrics to master dataset
            output_lyrics_file = os.path.join(lyrics_dir, f"{song_dir_name}_lyrics.txt")
            try:
                with open(lyrics_file, "r", encoding="utf-8") as f:
                    lyrics_content = f.read()
                
                with open(output_lyrics_file, "w", encoding="utf-8") as f:
                    f.write(lyrics_content)
                
                song_data["lyrics"] = lyrics_content
            except Exception as e:
                print(f"Error copying lyrics for {song_dir_name}: {e}")
    
    # Check for features.json
    features_file = song_dir_path / "features.json"
    if features_file.exists():
        song_data["has_features"] = True
        song_data["features_file"] = str(features_file.relative_to(song_dir_path))
        
        # Copy features to master dataset
        output_features_file = os.path.join(features_dir, f"{song_dir_name}_features.json")
        try:
            with open(features_file, "r", encoding="utf-8") as f:
                features_content = json.load(f)
            
            with open(output_features_file, "w", encoding="utf-8") as f:
                json.dump(features_content, f, indent=2)
            
            song_data["audio_features"] = features_content
        except Exception as e:
            print(f"Error copying features for {song_dir_name}: {e}")
    
    # Check for mel spectrogram
    mel_spectrogram_file = song_dir_path / "mel_spectrogram.png"
    mel_spectrogram_npy = song_dir_path / "mel_spectrogram.npy"
    if mel_spectrogram_file.exists() and mel_spectrogram_npy.exists():
        song_data["has_mel_spectrogram"] = True
        song_data["mel_spectrogram_path"] = str(mel_spectrogram_file.relative_to(song_dir_path))
        
        # Copy spectrogram to master dataset
        output_spectrogram_file = os.path.join(spectrograms_dir, f"{song_dir_name}_mel_spectrogram.png")
        output_spectrogram_npy = os.path.join(spectrograms_dir, f"{song_dir_name}_mel_spectrogram.npy")
        try:
            shutil.copy2(mel_spectrogram_file, output_spectrogram_file)
            shutil.copy2(mel_spectrogram_npy, output_spectrogram_npy)
        except Exception as e:
            print(f"Error copying spectrogram for {song_dir_name}: {e}")
    
    # Check for metadata
    metadata_dir_path = song_dir_path / "metadata"
    if metadata_dir_path.exists() and metadata_dir_path.is_dir():
        metadata_files = list(metadata_dir_path.glob("*.json"))
        if metadata_files:
            song_data["has_metadata"] = True
            metadata_file = metadata_files[0]
            song_data["metadata_file"] = str(metadata_file.relative_to(song_dir_path))
            
            # Copy metadata to master dataset
            output_metadata_file = os.path.join(metadata_dir, f"{song_dir_name}_metadata.json")
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata_content = json.load(f)
                
                with open(output_metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata_content, f, indent=2)
                
                song_data["metadata"] = metadata_content
            except Exception as e:
                print(f"Error copying metadata for {song_dir_name}: {e}")
    
    return song_data

def create_master_dataset(root_dir, output_dir, force=False):
    """Create a master dataset from all song directories."""
    # Get all song directories
    song_dirs = []
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and is_song_directory(item_path):
            song_dirs.append(item_path)
    
    print(f"Found {len(song_dirs)} song directories")
    
    # Process each song directory
    master_data = []
    for song_dir in song_dirs:
        song_data = process_song_directory(song_dir, output_dir, force)
        master_data.append(song_data)
    
    # Save master dataset
    master_dataset_file = os.path.join(output_dir, "master_dataset.json")
    with open(master_dataset_file, "w", encoding="utf-8") as f:
        json.dump(master_data, f, indent=2)
    
    print(f"Master dataset created at {output_dir}")
    print(f"Total songs processed: {len(master_data)}")

if __name__ == "__main__":
    args = parse_arguments()
    create_master_dataset(args.root_dir, args.output_dir, args.force)
