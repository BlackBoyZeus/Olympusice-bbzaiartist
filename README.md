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
- AI-powered music generation with text prompts

## Key Components

### Audio Processing
- `audio_processing.py`: Core audio processing utilities for feature extraction, standardization, and visualization
- `preprocess.py`: Audio preprocessing pipeline including stem separation and EnCodec encoding
- `prepare_music.py`: Music preparation pipeline for dataset creation

### Transcription and Analysis
- `transribe_vocals.py` / `convert-transcribe_vocals.py`: Vocal transcription tools using Whisper and Vosk
- `text2phone.py`: Text to phoneme conversion for vocal synthesis
- `metaessentia.py` / `meta.py`: Music feature extraction using Essentia and Librosa

### Generation
- `model.py`: Core music generation model using StripedHyena and S4 architectures
- `generate.py`: Music generation pipeline with text prompt interface
- `lyrics_generator.py`: AI-powered lyrics generation using Google's Gemini API

### Utilities
- `create_midi_zip_from_directory.py`: MIDI file packaging
- `test_spectrogram.py`: Spectrogram visualization testing

### API
- `api.py`: REST API for accessing the music generation system with FastAPI

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

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/olympusice-music-generator.git
cd olympusice-music-generator
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export GEMINI_API_KEY="your_gemini_api_key"
export A_AUDIO_DIR="/path/to/audio/files"
export MIDI_DIR="/path/to/midi/output"
export SPEC_DIR="/path/to/spectrogram/output"
export LYRICS_DIR="/path/to/lyrics/output"
export BASE_DIR="/path/to/base/directory"
export LOG_DIR="/path/to/logs"
export MODEL_DIR="/path/to/model/checkpoints"
export OUTPUT_DIR="/path/to/generated/output"
```

### Usage

#### Processing Audio Files

```bash
python preprocess.py
```

#### Generating Music

```bash
python generate.py --prompt "happy pop song in C major" --tempo 120 --key "C" --mode "major" --style "pop"
```

#### Running the API Server

```bash
python api.py
```

## API Endpoints

- `GET /generate_song`: Generate a song with parameters:
  - `prompt`: Text description of the song
  - `tempo`: BPM of the song
  - `key`: Musical key
  - `mode`: Major or minor
  - `style`: Musical style

## Dependencies

This project requires several Python libraries including:
- PyTorch
- Librosa
- Essentia
- Torchaudio
- Vosk (for speech recognition)
- Demucs (for stem separation)
- EnCodec (for audio compression)
- FastAPI (for API server)
- Google Generative AI (for lyrics generation)

## License

[License information to be added]

## Acknowledgments

- Facebook Research for EnCodec and Demucs
- HazyResearch for the S4 model implementation
- Google for the Gemini API
- OpenAI for Whisper ASR
- The Vosk project for speech recognition
