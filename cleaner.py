import os
import glob

def remove_mp3_files_from_tmp():
    """
    Remove all .mp3 files from the 'tmp' subfolder in the current directory.
    """
    # Define the path to the tmp folder
    tmp_folder = os.path.join(os.getcwd(), 'tmp')
    
    # Check if the tmp folder exists
    if not os.path.exists(tmp_folder):
        print(f"Folder '{tmp_folder}' does not exist.")
        return
    
    # Find all .mp3 files in the tmp folder
    mp3_files = glob.glob(os.path.join(tmp_folder, '*.mp3'))
    
    # Remove each file
    for file_path in mp3_files:
        try:
            os.remove(file_path)
            print(f"Removed: {file_path}")
        except Exception as e:
            print(f"Error removing {file_path}: {e}")
    
    print(f"Removed {len(mp3_files)} .mp3 file(s).")

