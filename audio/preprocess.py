import os
import glob
from concurrent.futures import ThreadPoolExecutor
from demucs import separate
from basic_pitch.inference import predict
import librosa
import numpy as np
from loguru import logger

AUDIO_DIR = "$BASE_DIR/audio"
MIDI_DIR = "$BASE_DIR/midi"
SPEC_DIR = "$BASE_DIR/spectrograms"
NUM_THREADS = 16  # Match M3 Pro’s cores
LOG_FILE = os.path.join("$LOG_DIR", "preprocess.log")

logger.add(LOG_FILE, rotation="500 MB")

def process_audio(audio_file):
    try:
        # Full source separation
        stem_dir = os.path.join(MIDI_DIR, "stems", os.path.splitext(os.path.basename(audio_file))[0])
        spec_stem_dir = os.path.join(SPEC_DIR, os.path.splitext(os.path.basename(audio_file))[0])
        os.makedirs(stem_dir, exist_ok=True)
        os.makedirs(spec_stem_dir, exist_ok=True)
        separate.main(["-o", stem_dir, audio_file])
        
        # Process each stem to MIDI and Mel spectrogram
        for stem in ["vocals", "drums", "bass", "other"]:
            stem_file = os.path.join(stem_dir, f"{stem}.wav")
            if os.path.exists(stem_file):
                # MIDI conversion
                midi_file = os.path.join(MIDI_DIR, f"{os.path.splitext(os.path.basename(audio_file))[0]}_{stem}.mid")
                midi_data, _, _ = predict(stem_file)
                midi_data.write(midi_file)
                
                # Mel spectrogram
                y, sr = librosa.load(stem_file, sr=44100)
                mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, hop_length=512)
                mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
                spec_file = os.path.join(spec_stem_dir, f"{stem}.npy")
                np.save(spec_file, mel_spec_db)
                logger.info(f"Processed {stem_file} -> {midi_file} and {spec_file}")
    except Exception as e:
        logger.error(f"Failed to process {audio_file}: {e}")

if __name__ == "__main__":
    audio_files = glob.glob(f"{AUDIO_DIR}/*.wav")
    logger.info(f"Found {len(audio_files)} audio files")
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        executor.map(process_audio, audio_files)
    logger.info("Preprocessing complete.")
