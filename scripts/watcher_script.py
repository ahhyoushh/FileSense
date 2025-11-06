from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from process_file import process_file
import os
import time
import argparse

parser = argparse.ArgumentParser(description="Process files in a directory.")
parser.add_argument("--dir", "-d", type=str, default="./files", help="Folder to organise.")

args = parser.parse_args()

files_dir = args.dir


class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        # event.src_path is the full path of the new file
        if event.is_directory:
            return

        file_path = event.src_path
        print(f"[+] New file detected: {os.path.basename(file_path)}")
        try:
            process_file(file_path)
        except Exception as e:
            print(f"[!] Error processing {file_path}: {e}")

if __name__ == "__main__":
    print("Starting folder watcher...")
    print(f"👀 Watching folder: {os.path.abspath(files_dir)}")
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, files_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(2)  # keeps the program running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()