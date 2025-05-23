import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import mido
import os
import subprocess
import librosa
from loguru import logger
from music21 import chord, scale, key, stream

LOG_FILE = os.path.join("$LOG_DIR", "generate.log")
SOUNDFONT_PATH = "$BASE_DIR/GeneralUser_GS_v1.471.sf2"
logger.add(LOG_FILE, rotation="500 MB")

def load_midi_data(midi_dir, track_type):
    midi_files = glob.glob(f"{midi_dir}/*_{track_type}.mid")
    sequences = []
    for midi_file in midi_files:
        midi = mido.MidiFile(midi_file)
        tracks = [t for t in midi.tracks if (track_type == "drums") == (mido.midifiles.MetaMessage('track_name', 'drums') in t)]
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
        sequences.append(np.array([notes, velocities, times]).T)
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
    s = stream.Stream()
    for note, vel, time in midi_data.T[:3]:
        if vel > 0 and note > 0:
            s.append(note.Note(note, quarterLength=time/480))
    k = s.analyze('key')
    scale_obj = scale.MajorScale(k.tonic)
    chords = [c for c in s.chordify().getElementsByClass(chord.Chord)]
    key_encoding = np.zeros(12)
    key_encoding[k.tonic.pitchClass] = 1
    scale_encoding = np.zeros(len(scale_obj.pitches))
    for p in scale_obj.pitches:
        scale_encoding[p.pitchClass] = 1
    chord_encoding = np.zeros(48)
    for c in chords[:16]:
        if c.isMajorTriad():
            chord_encoding[c.root().pitchClass * 4] = 1
        elif c.isMinorTriad():
            chord_encoding[c.root().pitchClass * 4 + 1] = 1
    return np.concatenate([key_encoding, scale_encoding, chord_encoding])

def generate_song(output_file="$OUTPUT_DIR/generated_song.wav"):
    try:
        model = load_model("$MODEL_DIR/hybrid_music_generator.h5")
        track_types = ["vocals", "drums", "bass", "other"]
        
        # Seed with sample data
        midi_data = np.concatenate([load_midi_data("$MIDI_DIR", t)[np.random.randint(len(load_midi_data("$MIDI_DIR", t)))] for t in track_types], axis=-1)
        spec_data = np.concatenate([load_spectrogram_data("$SPEC_DIR", t)[np.random.randint(len(load_spectrogram_data("$SPEC_DIR", t)))] for t in track_types], axis=-1)
        theory_data = np.concatenate([encode_music_theory(load_midi_data("$MIDI_DIR", t)[0], t) for t in track_types])
        
        # Generate structured song (intro, verse, chorus, verse, outro)
        structure = [("intro", 1), ("verse", 2), ("chorus", 2), ("verse", 2), ("outro", 1)]
        full_midi, full_spec = [], []
        seed_midi, seed_spec = midi_data[None, :16384, :], spec_data[None, :16384, :]
        for section, repeats in structure:
            for _ in range(repeats):
                generated = model.predict([seed_midi, seed_spec, theory_data])
                full_midi.append(generated[0, :, :12])  # MIDI (3 features * 4 tracks)
                full_spec.append(generated[0, :, 12:])  # Spectrograms (128 * 4 tracks)
                seed_midi = generated[:, -16384:, :12]
                seed_spec = generated[:, -16384:, 12:]
        
        # MIDI output for reference
        midi = mido.MidiFile()
        tempo = 120
        ticks_per_beat = 480
        for i, track_type in enumerate(track_types):
            track = mido.MidiTrack()
            midi.tracks.append(track)
            track.append(mido.MetaMessage('track_name', name=track_type))
            track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))
            time = 0
            for step in np.concatenate(full_midi, axis=0)[:, i*3:(i+1)*3]:
                note = int(step[0] * 127)
                velocity = int(step[1] * 127)
                delta = int(step[2] * ticks_per_beat / 4)
                if note > 0 and velocity > 0:
                    track.append(mido.Message('note_on', note=note, velocity=velocity, time=time))
                    track.append(mido.Message('note_off', note=note, velocity=0, time=delta or (ticks_per_beat // 4)))
                time = 0
        midi.save(f"{output_file}.mid")
        
        # Spectrogram to audio
        sr = 44100
        audio_tracks = []
        full_spec = np.concatenate(full_spec, axis=0)
        for i in range(len(track_types)):
            mel_spec = full_spec[:, i*128:(i+1)*128].T
            mel_spec = np.exp(librosa.db_to_power(mel_spec))
            audio = librosa.feature.inverse.mel_to_audio(mel_spec, sr=sr, hop_length=512)
            audio_tracks.append(audio)
        
        # Mix tracks
        mixed_audio = np.sum(audio_tracks, axis=0) / len(audio_tracks)
        librosa.output.write_wav(output_file, mixed_audio, sr)
        logger.info(f"Generated song saved to {output_file} and {output_file}.mid")
    except Exception as e:
        logger.error(f"Error during song generation: {e}")

if __name__ == "__main__":
    generate_song()
