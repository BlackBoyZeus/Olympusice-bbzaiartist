# OlympusIce Music Generator

OlympusIce is an advanced AI-powered music generation system that processes, analyzes, and generates music with various components.

## Project Overview

This project provides a complete pipeline for music processing, analysis, and generation, including:

- Audio preprocessing and standardization
- Vocal transcription and lyrics extraction
- Music feature extraction (melody, chord progression, structure)
- Stem separation (vocals, bass, drums, other instruments)
- Visualization generation (spectrograms, waveforms, chromagrams)
- MIDI file generation
- Music metadata management

## Key Components

### Audio Processing
- `audio_processing.py`: Core audio processing utilities
- `preprocess.py`: Audio preprocessing and standardization
- `prepare_music.py`: Music preparation pipeline

### Transcription and Analysis
- `transribe_vocals.py` / `convert-transcribe_vocals.py`: Vocal transcription tools
- `text2phone.py`: Text to phoneme conversion
- `metaessentia.py` / `meta.py`: Music feature extraction

### Generation
- `model.py`: Core music generation model
- `generate.py`: Music generation pipeline
- `lyrics_generator.py`: AI-powered lyrics generation

### Utilities
- `create_midi_zip_from_directory.py`: MIDI file packaging
- `test_spectrogram.py`: Spectrogram visualization testing

### API
- `api.py`: REST API for accessing the music generation system

## Project Structure

The repository contains processed music examples with the following structure:

```
./[Song Name] [ID]/
  ├── annotations/           # Song structure annotations
  ├── audio/                 # Processed audio files
  │   ├── htdemucs/          # Separated stems (bass, drums, other, vocals)
  │   ├── features.json      # Extracted audio features
  │   ├── lyrics.txt         # Transcribed lyrics
  │   ├── mel_spectrogram.*  # Mel spectrogram data and visualization
  │   └── standardized.wav   # Standardized audio file
  ├── dataset/               # Dataset information
  ├── lyrics/                # Processed lyrics
  ├── metadata/              # Song metadata
  ├── midi/                  # Generated MIDI files (melody, chord progression)
  ├── stems/                 # Separated audio stems
  └── visualizations/        # Visual representations of the audio
      ├── chromagram.png     # Chord visualization
      ├── mel_spectrogram.png # Frequency content visualization
      └── waveform.png       # Audio waveform visualization
```

## Model Architecture

OlympusIce uses a hierarchical music generation model with three main components:

1. **Structure Generator**: Transformer-based model that creates the overall song structure
2. **Phrase Generator**: StripedHyena layer that generates musical phrases
3. **EnCodec Generator**: StripedHyena layer that produces detailed audio encodings

The model leverages the S4 (Structured State Space Sequence) model for efficient long-range sequence modeling.

## Getting Started

### Prerequisites

- Python 3.10+
- PyTorch
- Librosa
- Essentia
- Torchaudio
- Vosk (for speech recognition)
- Demucs (for stem separation)
- EnCodec (for audio compression)
- Google Gemini API key (for lyrics generation)

## License

[License information to be added]
