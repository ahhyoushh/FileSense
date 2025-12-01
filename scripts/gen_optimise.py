# Gen folder_labels.json and optimise the prompt
from multhread import process_multiple
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
files_dir = os.path.join(BASE_DIR, "..", "files")

def gen_and_optimise():
    print(f"Generating folder_labels and optimising prompt: {files_dir} with 6 threads.")
    process_multiple(files_dir, 6, testing=False, allow_generation=True, TRAIN=True)