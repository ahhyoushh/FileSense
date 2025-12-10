from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from classify_process_file import process_file
import os
import time
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Process files in a directory.")
parser.add_argument("--dir", "-d", type=str, default="./files", help="Folder to organise.")
parser.add_argument("--wait-interval", type=float, default=0.5, help="Seconds between size checks.")
parser.add_argument("--max-checks", type=int, default=20, help="Max checks to wait for stable size.")
args = parser.parse_args()
files_dir = args.dir
WAIT_INTERVAL = args.wait_interval
MAX_CHECKS = args.max_checks

TEMP_SUFFIXES = (".crdownload", ".part", ".tmp", ".partial", ".download", ".~download", ".aria2")

def looks_temporary(name):
    return name.lower().endswith(TEMP_SUFFIXES)

class Watcher(FileSystemEventHandler):
    def _wait_and_process(self, path):
        """Inline simple waiter: block until file size stabilizes or timeout, then process."""
        name = os.path.basename(path)
        checks = 0
        prev_size = -1
        while checks < MAX_CHECKS:
            if os.path.exists(path):
                try:
                    cur = os.path.getsize(path)
                except OSError:
                    cur = -1
                if cur > 0 and cur == prev_size:
                    break
                prev_size = cur
            else:
                pass
            checks += 1
            time.sleep(WAIT_INTERVAL)

        if not os.path.exists(path):
            print(f"[!] Not found after wait: {name}")
            return

        if looks_temporary(name):
            print(f"[-] Skipping temp-like file name: {name}")
            return

        try:
            print(f"[+] Processing: {name}")
            process_file(path)
        except Exception as e:
            print(f"[!] Error processing {path}: {e}")

    def on_created(self, event):
        if event.is_directory:
            return
        path = event.src_path
        print(f"[+] Created event: {os.path.basename(path)}")
        self._wait_and_process(path)

    def on_moved(self, event):
        if event.is_directory:
            return
        dest = getattr(event, "dest_path", None) or getattr(event, "dest_path", None)
        if dest:
            print(f"[+] Moved event: {os.path.basename(event.src_path)} -> {os.path.basename(dest)}")
            self._wait_and_process(dest)

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    FLAG_FILE = BASE_DIR / "stop.flag"

    print("Starting folder watcher (simple mode)...")
    print(f"[WATCHING] {os.path.abspath(files_dir)}")

    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, files_dir, recursive=False)
    observer.start()
    try:
        while True:
            if FLAG_FILE.exists():
                print("[*] stop.flag detected — stopping watcher.")
                observer.stop()
                break
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
