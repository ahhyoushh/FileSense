from multhread import process_multiple
from classify_process_file import load_index_and_labels 
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
files_dir = os.path.join(BASE_DIR, "..", "files")

def train(files_dir, testing=False):
    print("Initializing Model and Index...")
    if not load_index_and_labels():
        print("Failed to initialize. Exiting.")
        sys.exit(1)

    print(f"Generating folder_labels and optimising prompt: {files_dir} with 6 threads.")
    process_multiple(files_dir, MAX_THREADS=6, testing=testing, allow_generation=True, TRAIN=True)
