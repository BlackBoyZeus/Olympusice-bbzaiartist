import os
import zipfile
from pathlib import Path

def create_zip_of_midi_files(source_dir, zip_path):
    """
    Loop through source_dir (and subdirectories), find all MIDI files,
    and create a ZIP file containing them.
    Handles duplicate filenames by appending a counter to the filename.
    """
    # Convert to Path objects
    source_dir = Path(source_dir)
    zip_path = Path(zip_path)

    # Ensure the source directory exists
    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"Directory {source_dir} does not exist or is not a directory")

    # Ensure the zip_path is a file, not a directory
    if zip_path.exists() and zip_path.is_dir():
        raise IsADirectoryError(f"Output path {zip_path} is a directory. Please specify a .zip file path (e.g., {zip_path}/midi_files.zip)")

    # Ensure the parent directory of the zip file exists
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    # Dictionary to track filenames and handle duplicates
    filename_counts = {}

    # Find all MIDI files in source_dir and its subdirectories
    midi_files = list(source_dir.rglob("*.mid")) + list(source_dir.rglob("*.midi"))
    if not midi_files:
        raise FileNotFoundError(f"No MIDI files found in {source_dir} or its subdirectories")
    print(f"Found {len(midi_files)} MIDI files in {source_dir}")

    # Create the ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for midi_path in midi_files:
            # Get the relative path of the MIDI file from the source directory
            relative_path = midi_path.relative_to(source_dir)
            
            # Check for duplicate filenames
            if str(relative_path) in filename_counts:
                filename_counts[str(relative_path)] += 1
                # Split the filename and extension
                base, ext = os.path.splitext(str(relative_path))
                # Create a new filename with the counter
                new_relative_path = f"{base}_{filename_counts[str(relative_path)]}{ext}"
            else:
                filename_counts[str(relative_path)] = 0
                new_relative_path = str(relative_path)

            # Add the file to the ZIP with the (possibly modified) relative path
            print(f"Adding: {midi_path} as {new_relative_path}")
            zipf.write(midi_path, new_relative_path)

    print(f"Created ZIP file: {zip_path} with {len(midi_files)} MIDI files")

# Example usage
if __name__ == "__main__":
    # Specify the source directory containing MIDI files
    source_directory = "/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)/music_generator"
    # Specify the output ZIP file path (must end with .zip)
    output_zip = "/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)/music_generator/muzic/midi_files.zip"
    create_zip_of_midi_files(source_directory, output_zip)