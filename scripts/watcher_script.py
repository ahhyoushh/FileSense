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
        ## CREATING stop.flag TO STOP THE SCRIPT ##
        FLAG_FILE = "stop.flag"
        while True:
            if os.path.exists(FLAG_FILE):
                print("🛑 Stop flag detected, shutting down...")
                os.remove(FLAG_FILE)
                break
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

## CREATING stop.flag TO STOP THE SCRIPT ##
FLAG_FILE = "stop.flag"

while True:
    if os.path.exists(FLAG_FILE):
        print("🛑 Stop flag detected, shutting down...")
        os.remove(FLAG_FILE)
        break
    # your normal monitoring logic here
    time.sleep(2)