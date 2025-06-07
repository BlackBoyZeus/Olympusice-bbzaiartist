#!/usr/bin/env python3
"""
Script to process audio files and generate spectrograms.
This is a simplified version of meta.py that focuses on generating spectrograms.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use('Agg')  # Ensure matplotlib doesn't try to open display
import matplotlib.pyplot as plt

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process audio files and generate spectrograms")
    parser.add_argument("--audio-file", type=str, required=True, help="Path to audio file")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory for spectrograms")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing files")
    return parser.parse_args()

def load_audio(audio_path):
    """Load audio file using librosa."""
    print(f"Loading audio: {audio_path}")
    try:
        y, sr = librosa.load(str(audio_path), sr=None, mono=True)
        duration = librosa.get_duration(y=y, sr=sr) if y is not None else 0
        print(f"Loaded audio: {audio_path} (Sample Rate: {sr}, Duration: {duration:.2f}s)")
        return y, sr
    except Exception as e:
        print(f"Failed to load audio {audio_path}: {e}")
        return None, None

def plot_spectrogram(y, sr, output_path):
    """Generate and save a mel spectrogram."""
    try:
        print(f"Generating spectrogram: {output_path}")
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        plt.figure(figsize=(12, 4))
        librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', fmax=8000)
        plt.colorbar(format='%+2.0f dB')
        plt.title('Mel Spectrogram')
        plt.tight_layout()
        plt.savefig(str(output_path))
        plt.close()
        print(f"Spectrogram saved to {output_path}")
        
        # Also save the numpy array for later use
        np_path = output_path.with_suffix('.npy')
        np.save(np_path, S)
        print(f"Spectrogram data saved to {np_path}")
        
        return True
    except Exception as e:
        print(f"Failed to plot spectrogram: {e}")
        plt.close()
        return False

def plot_waveform(y, sr, output_path):
    """Generate and save a waveform plot."""
    try:
        print(f"Generating waveform: {output_path}")
        plt.figure(figsize=(12, 3))
        librosa.display.waveshow(y, sr=sr, alpha=0.8)
        plt.title('Waveform')
        plt.tight_layout()
        plt.savefig(str(output_path))
        plt.close()
        print(f"Waveform saved to {output_path}")
        return True
    except Exception as e:
        print(f"Failed to plot waveform: {e}")
        plt.close()
        return False

def plot_chromagram(y, sr, output_path):
    """Generate and save a chromagram plot."""
    try:
        print(f"Generating chromagram: {output_path}")
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=1024)
        plt.figure(figsize=(12, 4))
        librosa.display.specshow(chroma, sr=sr, y_axis='chroma', x_axis='time', hop_length=1024)
        plt.colorbar()
        plt.title('Chromagram (CQT)')
        plt.tight_layout()
        plt.savefig(str(output_path))
        plt.close()
        print(f"Chromagram saved to {output_path}")
        return True
    except Exception as e:
        print(f"Failed to plot chromagram: {e}")
        plt.close()
        return False

def process_audio_file(audio_file, output_dir, force=False):
    """Process an audio file and generate visualizations."""
    audio_path = Path(audio_file)
    output_dir = Path(output_dir)
    
    # Create output directories
    output_dir.mkdir(exist_ok=True)
    visuals_dir = output_dir / "visuals"
    visuals_dir.mkdir(exist_ok=True)
    
    # Load audio
    y, sr = load_audio(audio_path)
    if y is None or sr is None:
        print(f"Failed to load audio: {audio_path}")
        return False
    
    # Generate spectrogram
    spectrogram_path = output_dir / "mel_spectrogram.png"
    if not spectrogram_path.exists() or force:
        if not plot_spectrogram(y, sr, spectrogram_path):
            print(f"Failed to generate spectrogram for {audio_path}")
    
    # Generate waveform
    waveform_path = visuals_dir / "waveform.png"
    if not waveform_path.exists() or force:
        if not plot_waveform(y, sr, waveform_path):
            print(f"Failed to generate waveform for {audio_path}")
    
    # Generate chromagram
    chromagram_path = visuals_dir / "chromagram.png"
    if not chromagram_path.exists() or force:
        if not plot_chromagram(y, sr, chromagram_path):
            print(f"Failed to generate chromagram for {audio_path}")
    
    # Generate spectrogram in visuals directory
    visuals_spectrogram_path = visuals_dir / "spectrogram.png"
    if not visuals_spectrogram_path.exists() or force:
        if not plot_spectrogram(y, sr, visuals_spectrogram_path):
            print(f"Failed to generate spectrogram in visuals directory for {audio_path}")
    
    # Create features.json
    features_path = output_dir / "features.json"
    if not features_path.exists() or force:
        try:
            # Extract basic features
            duration = librosa.get_duration(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            features = {
                "duration": float(duration),
                "sample_rate": sr,
                "tempo": float(tempo),
                "spectrogram_path": str(spectrogram_path.relative_to(output_dir)),
                "waveform_path": str(waveform_path.relative_to(output_dir)),
                "chromagram_path": str(chromagram_path.relative_to(output_dir)),
                "processed_at": "2025-06-06T16:30:00Z"
            }
            
            with open(features_path, "w") as f:
                json.dump(features, f, indent=2)
            
            print(f"Features saved to {features_path}")
        except Exception as e:
            print(f"Failed to create features.json: {e}")
    
    print(f"Processing complete for {audio_path}")
    return True

if __name__ == "__main__":
    args = parse_arguments()
    process_audio_file(args.audio_file, args.output_dir, args.force)
