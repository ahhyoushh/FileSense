import threading
import os
from process_file import process_file, files_dir 
import time

MAX_THREADS = 6  # max concurrent threads

def main():
    files = [
        os.path.join(files_dir, f)
        for f in os.listdir(files_dir)
        if os.path.isfile(os.path.join(files_dir, f))
    ]
    print(f"Found {len(files)} files to process.\n")

    start_time = time.time()
    threads = []
    for file_path in files:
        # wait if too many threads already running
        while threading.active_count() > MAX_THREADS:
            time.sleep(0.1)

        # start a new thread
        t = threading.Thread(target=process_file, args=(file_path,))
        t.start()
        threads.append(t)

        # show active thread count (minus main thread itself)
        active = threading.active_count() - 1
        print(f"[+] Started thread for {os.path.basename(file_path)} | Active threads: {active}")

    # wait for all threads to finish
    for t in threads:
        t.join()

    print(f"\n All files processed in {time.time() - start_time:.2f}s\n")

if __name__ == "__main__":
    main()