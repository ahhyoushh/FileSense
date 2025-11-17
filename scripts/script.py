from multhread import process_multiple
import argparse

parser = argparse.ArgumentParser(description="Process files in a directory concurrently.")
parser.add_argument("--dir", "-d", type=str, default="./files", help="Folder to organise.")
parser.add_argument("--threads", "-t", type=int, default=6, help="Maximum number of concurrent threads.")

args = parser.parse_args()
files_dir = args.dir
MAX_THREADS = args.threads

if __name__ == "__main__":
    print(f"Processing files in directory: {files_dir} with {MAX_THREADS} threads.")
    process_multiple(files_dir, MAX_THREADS, testing=True)