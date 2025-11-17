import threading
import os
from classify_process_file import process_file
import time


def process_multiple(files_dir, MAX_THREADS, testing=False):
    files = [
        os.path.join(files_dir, f)
        for f in os.listdir(files_dir)
        if os.path.isfile(os.path.join(files_dir, f))
    ]
    print(f"Found {len(files)} files to process.\n")

    start_time = time.time()
    threads = []
    for file_path in files:
        while threading.active_count() > MAX_THREADS:
            time.sleep(0.1)

        t = threading.Thread(target=process_file, args=(file_path,testing))
        t.start()
        threads.append(t)

        active = threading.active_count() - 1
        print(f"[+] Started thread for {os.path.basename(file_path)} | Active threads: {active}")

    for t in threads:
        t.join()

    print(f"\n All files processed in {time.time() - start_time:.2f}s\n")

