import tensorflow as tf
from tensorflow.keras import layers, models
from loguru import logger
import os
import glob
import mido
import numpy as np
from music21 import chord, scale, key, stream

LOG_FILE = os.path.join("$LOG_DIR", "model.log")
logger.add(LOG_FILE, rotation="500 MB")

def is_drum_track(track):
    for msg in track:
        if msg.type == 'program_change' and msg.program >= 112 and msg.program <= 127:
            return True
        if msg.is_cc(10):
            return True
    return False

def load_midi_data(midi_dir, track_type):
    midi_files = glob.glob(f"{midi_dir}/*_{track_type}.mid")
    sequences = []
    for midi_file in midi_files:
        try:
            midi = mido.MidiFile(midi_file)
            tracks = [track for track in midi.tracks if (track_type == "drums") == is_drum_track(track)]
            merged_track = mido.MidiTrack()
            for track in tracks:
                merged_track.extend(track)
            
            notes, velocities, times = [], [], []
            time = 0
            for msg in merged_track:
                time += msg.time
                if msg.type == 'note_on':
                    notes.append(msg.note)
                    velocities.append(msg.velocity)
                    times.append(time)
                elif msg.type == 'note_off':
                    notes.append(msg.note)
                    velocities.append(0)
                    times.append(time)
            
            sequence_length = 16384
            if len(notes) < sequence_length:
                notes += [0] * (sequence_length - len(notes))
                velocities += [0] * (sequence_length - len(velocities))
                times += [0] * (sequence_length - len(times))
            else:
                notes = notes[:sequence_length]
                velocities = velocities[:sequence_length]
                times = times[:sequence_length]
            
            sequence = np.array([notes, velocities, times]).T
            sequences.append(sequence)
        except Exception as e:
            logger.error(f"Error processing {midi_file}: {e}")
    return np.array(sequences)

def load_spectrogram_data(spec_dir, track_type):
    spec_files = glob.glob(f"{spec_dir}/*_{track_type}.npy")
    sequences = []
    for spec_file in spec_files:
        spec = np.load(spec_file)
        sequence_length = 16384
        if spec.shape[1] < sequence_length:
            spec = np.pad(spec, ((0, 0), (0, sequence_length - spec.shape[1])), mode='constant')
        else:
            spec = spec[:, :sequence_length]
        sequences.append(spec.T)
    return np.array(sequences)

def encode_music_theory(midi_data, track_type):
    # Analyze MIDI for key, scale, and chords using music21
    s = stream.Stream()
    for note, vel, time in midi_data.T[:3]:  # Use first 3 columns (notes, velocities, times)
        if vel > 0 and note > 0:
            s.append(note.Note(note, quarterLength=time/480))  # Assume 120 BPM, 480 ticks/quarter
    k = s.analyze('key')
    scale_obj = scale.MajorScale(k.tonic)
    chords = [c for c in s.chordify().getElementsByClass(chord.Chord)]
    # Encode as one-hot vectors or embeddings
    key_encoding = np.zeros(12)  # 12 semitones for key
    key_encoding[k.tonic.pitchClass] = 1
    scale_encoding = np.zeros(len(scale_obj.pitches))  # Simplified scale encoding
    for p in scale_obj.pitches:
        scale_encoding[p.pitchClass] = 1
    chord_encoding = np.zeros(48)  # 4 common chord types (major, minor, etc.) per key
    for c in chords[:16]:  # Limit to first 16 chords for sequence length
        if c.isMajorTriad():
            chord_encoding[c.root().pitchClass * 4] = 1
        elif c.isMinorTriad():
            chord_encoding[c.root().pitchClass * 4 + 1] = 1
    return np.concatenate([key_encoding, scale_encoding, chord_encoding])

def striped_hyena_layer(inputs, filters, kernel_size=3):
    conv = layers.Conv1D(filters, kernel_size, padding='causal', activation='relu')(inputs)
    gate = layers.Conv1D(filters, kernel_size, padding='causal', activation='sigmoid')(inputs)
    gated_conv = layers.Multiply()([conv, gate])
    recurrent = layers.SimpleRNN(filters, return_sequences=True)(gated_conv)
    return layers.Add()([gated_conv, recurrent])

def build_hybrid_music_generator(seq_length=16384, n_mels=128, feature_dim=3, num_tracks=4):
    # MIDI input (notes, velocities, times)
    midi_input = layers.Input(shape=(seq_length, feature_dim * num_tracks))
    # Spectrogram input (Mel spectrograms)
    spec_input = layers.Input(shape=(seq_length, n_mels * num_tracks))
    # Music theory input (key, scale, chords)
    theory_input = layers.Input(shape=(64,))  # Encoded music theory (key, scale, chords)
    
    # Process MIDI
    midi_outputs = []
    for i in range(num_tracks):
        track_input = midi_input[:, :, i*feature_dim:(i+1)*feature_dim]
        x = layers.Embedding(128, 32)(tf.cast(track_input[:, :, 0], dtype=tf.int32))
        x = layers.Concatenate()([x, track_input[:, :, 1:]])
        x = striped_hyena_layer(x, 256)
        x = striped_hyena_layer(x, 128)
        midi_outputs.append(layers.Dense(feature_dim, activation='linear')(x))
    midi_fused = layers.Concatenate(axis=-1)(midi_outputs)
    
    # Process spectrograms
    spec_outputs = []
    for i in range(num_tracks):
        track_input = spec_input[:, :, i*n_mels:(i+1)*n_mels]
        x = layers.Conv1D(256, 3, padding='causal', activation='relu')(track_input)
        x = layers.LSTM(128, return_sequences=True)(x)
        spec_outputs.append(layers.Conv1D(n_mels, 1, activation='linear')(x))
    spec_fused = layers.Concatenate(axis=-1)(spec_outputs)
    
    # Incorporate music theory
    theory_dense = layers.Dense(64, activation='relu')(theory_input)
    theory_expanded = layers.RepeatVector(seq_length)(theory_dense)
    theory_processed = layers.Conv1D(128, 1, activation='relu')(theory_expanded)
    
    # Fusion
    fused = layers.Concatenate(axis=-1)([midi_fused, spec_fused, theory_processed])
    final_output = layers.Conv1D(feature_dim * num_tracks, 1, activation='linear')(fused)
    
    return models.Model([midi_input, spec_input, theory_input], final_output, name="hybrid_music_generator")

def train_model():
    model = build_hybrid_music_generator()
    model.compile(optimizer='adam', loss='mse')
    track_types = ["vocals", "drums", "bass", "other"]
    
    # Load MIDI and spectrogram data
    midi_data = np.concatenate([load_midi_data("$MIDI_DIR", t) for t in track_types], axis=-1)
    spec_data = np.concatenate([load_spectrogram_data("$SPEC_DIR", t) for t in track_types], axis=-1)
    
    # Encode music theory for each sample
    theory_data = []
    for t in track_types:
        midi_samples = load_midi_data("$MIDI_DIR", t)
        theory_encodings = np.array([encode_music_theory(sample, t) for sample in midi_samples])
        theory_data.append(theory_encodings)
    theory_data = np.concatenate(theory_data, axis=0)
    
    if midi_data.size == 0 or spec_data.size == 0 or theory_data.size == 0:
        logger.error("No data found. Check preprocessing.")
        return
    
    model.fit([midi_data, spec_data, theory_data], midi_data, epochs=20, batch_size=2, verbose=1)
    model.save("$MODEL_DIR/hybrid_music_generator.h5")
    logger.info("Hybrid model training completed")

if __name__ == "__main__":
    train_model()
