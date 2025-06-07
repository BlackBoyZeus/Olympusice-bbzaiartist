#!/usr/bin/env python3
"""
Data preparation script for music generation models.
This script prepares data from the master dataset for model training.
"""

import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path
import librosa
import matplotlib.pyplot as plt
from tqdm import tqdm

def parse_arguments():
    parser = argparse.ArgumentParser(description="Prepare data for model training")
    parser.add_argument("--master-dataset", type=str, 
                        default="/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)Main/music_generator/master_dataset",
                        help="Path to master dataset directory")
    parser.add_argument("--output-dir", type=str, 
                        default="/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)Main/music_generator/training_data",
                        help="Output directory for prepared data")
    parser.add_argument("--format", type=str, choices=["numpy", "tfrecord", "json"], default="numpy",
                        help="Output format for the prepared data")
    parser.add_argument("--feature-type", type=str, choices=["mel_spectrogram", "mfcc", "chroma"], default="mel_spectrogram",
                        help="Type of features to extract")
    parser.add_argument("--segment-duration", type=float, default=5.0,
                        help="Duration of audio segments in seconds")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing files")
    return parser.parse_args()

def load_master_dataset(master_dataset_path):
    """Load the master dataset JSON file."""
    master_json_path = os.path.join(master_dataset_path, "master_dataset.json")
    try:
        with open(master_json_path, "r") as f:
            master_data = json.load(f)
        print(f"Loaded master dataset with {len(master_data)} songs")
        return master_data
    except Exception as e:
        print(f"Error loading master dataset: {e}")
        return None

def load_spectrogram(spectrogram_path):
    """Load a spectrogram from a numpy file."""
    try:
        return np.load(spectrogram_path)
    except Exception as e:
        print(f"Error loading spectrogram {spectrogram_path}: {e}")
        return None

def extract_features(audio_path, feature_type, segment_duration=None):
    """Extract features from an audio file."""
    try:
        y, sr = librosa.load(audio_path, sr=None)
        
        if segment_duration is not None:
            # Convert segment duration to samples
            segment_samples = int(segment_duration * sr)
            
            # If audio is shorter than segment duration, pad with zeros
            if len(y) < segment_samples:
                y = np.pad(y, (0, segment_samples - len(y)))
            
            # If audio is longer than segment duration, take the first segment
            elif len(y) > segment_samples:
                y = y[:segment_samples]
        
        if feature_type == "mel_spectrogram":
            features = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
            features_db = librosa.power_to_db(features, ref=np.max)
            return features_db
        
        elif feature_type == "mfcc":
            features = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            return features
        
        elif feature_type == "chroma":
            features = librosa.feature.chroma_cqt(y=y, sr=sr)
            return features
        
        else:
            print(f"Unknown feature type: {feature_type}")
            return None
    
    except Exception as e:
        print(f"Error extracting features from {audio_path}: {e}")
        return None

def segment_spectrogram(spectrogram, segment_frames=128):
    """Segment a spectrogram into fixed-size chunks."""
    # If spectrogram is shorter than segment_frames, pad with zeros
    if spectrogram.shape[1] < segment_frames:
        padding = np.zeros((spectrogram.shape[0], segment_frames - spectrogram.shape[1]))
        spectrogram = np.hstack((spectrogram, padding))
    
    # Segment the spectrogram
    segments = []
    for i in range(0, spectrogram.shape[1], segment_frames):
        if i + segment_frames <= spectrogram.shape[1]:
            segment = spectrogram[:, i:i+segment_frames]
            segments.append(segment)
    
    return segments

def prepare_data(master_data, master_dataset_path, output_dir, feature_type="mel_spectrogram", 
                segment_duration=5.0, output_format="numpy", force=False):
    """Prepare data for model training."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectories for different data types
    features_dir = os.path.join(output_dir, "features")
    labels_dir = os.path.join(output_dir, "labels")
    metadata_dir = os.path.join(output_dir, "metadata")
    
    os.makedirs(features_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    
    # Process each song
    all_features = []
    all_labels = []
    all_metadata = []
    
    for song in tqdm(master_data, desc="Processing songs"):
        song_name = song["song_name"]
        song_dir = song.get("directory", "")
        
        # Skip songs without directory information
        if not song_dir:
            print(f"Skipping {song_name}: No directory information")
            continue
        
        # Check for mel spectrogram
        if feature_type == "mel_spectrogram" and song.get("has_mel_spectrogram", False):
            # Load from master dataset if available
            spectrogram_path = os.path.join(master_dataset_path, "spectrograms", f"{song_name}_mel_spectrogram.npy")
            if os.path.exists(spectrogram_path):
                features = load_spectrogram(spectrogram_path)
            else:
                # Try loading from original location
                original_path = song.get("mel_spectrogram_path", "")
                if original_path and os.path.exists(os.path.join(song_dir, original_path)):
                    features = load_spectrogram(os.path.join(song_dir, original_path))
                else:
                    print(f"Mel spectrogram not found for {song_name}")
                    features = None
        else:
            # Extract features from audio file
            audio_files = list(Path(os.path.join(song_dir, "audio")).glob("*.mp3")) + \
                         list(Path(os.path.join(song_dir, "audio")).glob("*.wav"))
            
            if not audio_files:
                print(f"No audio files found for {song_name}")
                continue
            
            # Use the first audio file
            audio_file = audio_files[0]
            features = extract_features(audio_file, feature_type, segment_duration)
        
        if features is None:
            print(f"Failed to extract features for {song_name}")
            continue
        
        # Get labels (lyrics)
        lyrics = song.get("lyrics", "")
        
        # Segment features if needed
        if segment_duration is not None:
            feature_segments = segment_spectrogram(features)
            
            # Save each segment
            for i, segment in enumerate(feature_segments):
                segment_name = f"{song_name}_segment_{i}"
                
                # Save features
                if output_format == "numpy":
                    np.save(os.path.join(features_dir, f"{segment_name}.npy"), segment)
                
                # Add to lists
                all_features.append(segment_name)
                all_labels.append(lyrics)
                all_metadata.append({
                    "song_name": song_name,
                    "segment_index": i,
                    "segment_duration": segment_duration,
                    "feature_type": feature_type
                })
        else:
            # Save full features
            if output_format == "numpy":
                np.save(os.path.join(features_dir, f"{song_name}.npy"), features)
            
            # Add to lists
            all_features.append(song_name)
            all_labels.append(lyrics)
            all_metadata.append({
                "song_name": song_name,
                "feature_type": feature_type
            })
    
    # Save metadata
    with open(os.path.join(metadata_dir, "metadata.json"), "w") as f:
        json.dump({
            "features": all_features,
            "labels": all_labels,
            "metadata": all_metadata
        }, f, indent=2)
    
    # Save labels
    with open(os.path.join(labels_dir, "labels.json"), "w") as f:
        json.dump({
            "song_names": all_features,
            "lyrics": all_labels
        }, f, indent=2)
    
    print(f"Data preparation complete. Processed {len(all_features)} segments from {len(master_data)} songs.")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    args = parse_arguments()
    
    # Load master dataset
    master_data = load_master_dataset(args.master_dataset)
    if master_data is None:
        sys.exit(1)
    
    # Prepare data
    prepare_data(
        master_data,
        args.master_dataset,
        args.output_dir,
        args.feature_type,
        args.segment_duration,
        args.format,
        args.force
    )
