import glob
import os


def remove_audio_files_from_tmp() -> None:
    """
    Remove all .mp3/.wav files from the 'tmp' subfolder in the current directory.
    """
    # Define the path to the tmp folder
    tmp_folder = os.path.join(os.getcwd(), "tmp")

    # Check if the tmp folder exists
    if not os.path.exists(tmp_folder):
        print(f"Folder '{tmp_folder}' does not exist.")
        return

    # Find all .mp3 files in the tmp folder
    mp3_files = glob.glob(os.path.join(tmp_folder, "*.mp3"))
    wav_files = glob.glob(os.path.join(tmp_folder, "*.wav"))
    all_files = mp3_files + wav_files
    # Remove each file
    for file_path in all_files:
        try:
            os.remove(file_path)
            print(f"Removed: {file_path}")
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

    print(f"Removed {len(all_files)} temp audio file(s).")
