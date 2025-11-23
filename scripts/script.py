import os
import argparse
import sys
from multhread import process_multiple
from classify_process_file import process_file, load_index_and_labels 

test = True
parser = argparse.ArgumentParser(description="Process files in a directory concurrently.")
parser.add_argument("--dir", "-d", type=str, default="./files", help="Folder to organise.")
parser.add_argument("--threads", "-t", type=int, default=6, help="Maximum number of concurrent threads.")
parser.add_argument("--single-thread", action="store_true", help="Run in single-threaded mode instead of multi-threaded.")
parser.add_argument("--no-generation", action="store_true", help="Do not allow generation if classification fails.")
args = parser.parse_args()

if __name__ == "__main__":
    if not load_index_and_labels():
        print("\n[!] Initialization failed. Cannot start file processing. Exiting.")
        sys.exit(1) 

    files_dir = args.dir
    MAX_THREADS = args.threads

    if not os.path.isdir(files_dir):
        print(f"Error: Directory not found at '{files_dir}'")
        sys.exit(1)

    if args.single_thread:
        print(f"Processing files in directory: {files_dir} in SINGLE-THREADED mode.")
        files = [
            os.path.join(files_dir, f)
            for f in os.listdir(files_dir)
            if os.path.isfile(os.path.join(files_dir, f))
        ]
        if not files:
            print("No files to process.")
        else:
            for file_path in files:
                process_file(file_path, testing=test, allow_generation=not args.no_generation)
    else:
        print(f"Processing files in directory: {files_dir} with {MAX_THREADS} threads.")
        process_multiple(files_dir, MAX_THREADS, testing=test, allow_generation=not args.no_generation)

