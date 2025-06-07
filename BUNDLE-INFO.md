# Music Generator Bundle Information

## Bundle File Location

The complete repository bundle file is available at:
`/Users/blblackboyzeusackboyzeus/BBZ(AiArtist)Main/music-generator-bundle-with-madison-june.bundle`

## How to Use This Bundle

1. Clone the repository from AWS CodeCommit:
   ```bash
   git clone ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/music-generator
   cd music-generator
   ```

2. Unbundle the bundle file:
   ```bash
   git bundle unbundle /path/to/music-generator-bundle-with-madison-june.bundle
   ```

3. Check out the madison-june-update branch:
   ```bash
   git checkout madison-june-update
   ```

## Contents

This bundle includes:
- Madison June song files
- Audio processing scripts
- Data preparation scripts
- Master dataset creation scripts
- Training data generation scripts
- All large audio and model files

## AWS CodeCommit Status

The following files have been successfully pushed to AWS CodeCommit:

1. **Data Processing Scripts**:
   - `process_audio.py`: For processing audio files and generating spectrograms
   - `create_master_dataset.py`: For creating a master dataset from all song directories
   - `data_preparation.py`: For preparing data for model training

2. **Madison June Song Files**:
   - `data/catalog/Madison June [MJ2023]/features/features.json`: Contains audio metadata
   - `data/catalog/Madison June [MJ2023]/lyrics/lyrics.txt`: Contains the song lyrics

3. **Documentation**:
   - `README.md`: Updated with project information
   - `project_summary.md`: Contains a summary of the project updates

A pull request (#3) has been created in AWS CodeCommit and is ready for review.

## Note

The bundle file is 11.3 MB in size and contains all the necessary files to work with the music generator project.

