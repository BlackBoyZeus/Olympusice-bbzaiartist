import os
import json
import vosk
import wave
import multiprocessing
from pydub import AudioSegment

# Set the directory where the audio files are located
AUDIO_DIR = "/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)/music_generator"
MODEL_PATH = "/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)/music_generator/vosk-model-en-us-0.22-lgraph"

# List of song directory names
SONG_DIR_NAMES = [
    "05’ Zuck [ZsOtqU3-HXs]", "3peat [gq1eofElbwQ]", "3peat [icokPtJYGI0]", "A Word [m3LoKaAsWr4]",
    "Before They Called Me Potus (Medley) [Pomac4FafcM]", "Blue [dXHGW86pyuo]", "Caught Up [xqUaqeQ2vTo]",
    "Disney 713 [tK-yvwgXvQw]", "Falling [dmvPkL4dr9Q]", "Friended [SVuOI1Xj4pw]", "Full Circle [6LZokJkBVeI]",
    "Kobe Era [lV5enN6aqNw]", "Kylian Mbappe (Boston) [ySxBGpF9jqc]", "Kylian Mbappe (Houston) [tQ8zqN65w5U]",
    "Kylian Mbappe [wHyWd-zUp7c]", "Love Dreams [YK0HONWHlIk]", "Love Dreams [xxlTAYf-t1o]",
    "Magnetism [ok72CYJZd0k]", "MewTwo [KT1T4cAz8d0]", "Michelin Chef [fXxEqOINW8E]",
    "Michelin Star Marsmix (Bonus) [laOlvd6sNrQ]", "New Font [czYj2TxIRH8]", "New Years Without Eve [CfwOillWux4]",
    "Noahs Arc [0JCR94rF5qI]", "Patronus Charm (Bonus) [o5oH_tt6sB0]", "StarLight ~ by POTUS： A Rendition [dQX8wPXuBH4]",
    "Sunday Blues (Bonus) [l9pkSqWFoUc]", "Taste It [dpD_8-E1iC4]", "Thank God Im [sT0horz7Pk8]",
    "Zepeto [9LaebRCA3WM]", "Zuckbergian [lj1YVJBrEDQ]"
]

def convert_to_pcm_mono(input_path, output_path):
    """Converts an audio file to WAV format with 16-bit PCM mono"""
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        audio.export(output_path, format="wav")
        print(f"Converted: {input_path} -> {output_path}")
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False

def transcribe_audio(audio_path, model_path):
    """Transcribes speech from a WAV file using Vosk"""
    try:
        model = vosk.Model(model_path)
        wf = wave.open(audio_path, "rb")
        
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError(f"Invalid format: {audio_path} (Must be 16-bit PCM mono)")
        
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        results = []
        
        # Process in chunks for better memory management
        buffer_size = 16000
        while True:
            data = wf.readframes(buffer_size)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                results.append(result.get("text", ""))
        
        final_result = json.loads(rec.FinalResult())
        results.append(final_result.get("text", ""))
        
        transcription = " ".join(results).strip()
        return audio_path, transcription if transcription else "[No transcription available]"
    except Exception as e:
        print(f"Error transcribing {audio_path}: {e}")
        return audio_path, "[Error]"

def process_song_directory(args):
    """Process a single song directory"""
    song_dir_name, model_path = args
    song_dir_path = os.path.join(AUDIO_DIR, song_dir_name)
    
    if not os.path.exists(song_dir_path):
        print(f"Directory not found: {song_dir_path}")
        return song_dir_name, "[Directory not found]"
    
    # Set up directory structure
    audio_dir = os.path.join(song_dir_path, "audio")
    dataset_dir = os.path.join(song_dir_path, "dataset")
    features_dir = os.path.join(dataset_dir, "features")
    
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(features_dir, exist_ok=True)
    
    # Source and target paths
    vocals_wav = os.path.join(audio_dir, "htdemucs", song_dir_name, "vocals.wav")
    main_wav = os.path.join(audio_dir, f"{song_dir_name}.wav")
    converted_path = os.path.join(audio_dir, "vocals_converted.wav")
    
    # Determine source file
    source_path = vocals_wav if os.path.exists(vocals_wav) else main_wav
    
    if not os.path.exists(source_path):
        print(f"No vocals.wav or main WAV found in {song_dir_name}")
        return song_dir_name, "[No audio file found]"
    
    # Convert and transcribe
    if convert_to_pcm_mono(source_path, converted_path):
        audio_path, lyrics = transcribe_audio(converted_path, model_path)
        
        # Save lyrics in both audio/ and dataset/ directories
        audio_lyrics_path = os.path.join(audio_dir, "lyrics.txt")
        dataset_lyrics_path = os.path.join(dataset_dir, "lyrics.txt")
        
        with open(audio_lyrics_path, "w") as f:
            f.write(lyrics)
        with open(dataset_lyrics_path, "w") as f:
            f.write(lyrics)
        
        print(f"Saved lyrics for {song_dir_name} to: {audio_lyrics_path}")
        return song_dir_name, lyrics
    else:
        return song_dir_name, "[Conversion failed]"

def main():
    # Set Vosk logging level
    vosk.SetLogLevel(0)  # Reduce verbosity
    
    # Delete existing lyrics files
    print("Deleting existing lyrics files...")
    for song_dir_name in SONG_DIR_NAMES:
        song_dir_path = os.path.join(AUDIO_DIR, song_dir_name)
        for root, _, files in os.walk(song_dir_path):
            for file in files:
                if file.lower() == "lyrics.txt":
                    os.remove(os.path.join(root, file))
                    print(f"Deleted: {os.path.join(root, file)}")
    
    print(f"Found {len(SONG_DIR_NAMES)} song directories to process.")
    
    # Set up multiprocessing
    num_cores = max(1, multiprocessing.cpu_count() // 2)  # Use half the cores to reduce memory pressure
    print(f"Using {num_cores} CPU cores for processing.")
    
    with multiprocessing.Pool(processes=num_cores) as pool:
        results = pool.map(
            process_song_directory,
            [(song_dir_name, MODEL_PATH) for song_dir_name in SONG_DIR_NAMES]
        )
    
    # Print summary
    print("\nProcessing Summary:")
    for song_dir_name, lyrics in results:
        print(f"\n{song_dir_name}:")
        print(f"{lyrics[:100]}..." if len(lyrics) > 100 else lyrics)
        print("-" * 50)


if __name__ == "__main__":
    main()