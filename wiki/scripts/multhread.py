import concurrent.futures
import os
from classify_process_file import process_file
import time


def process_multiple(files_dir, MAX_THREADS, testing=False, allow_generation=True, sorted_dir=None):
    files = [
        os.path.join(files_dir, f)
        for f in os.listdir(files_dir)
        if os.path.isfile(os.path.join(files_dir, f))
    ]
    print(f"Found {len(files)} files to process.\n")

    start_time = time.time()

    # Use ThreadPoolExecutor for efficient thread management
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for file_path in files:
            # Submit tasks to the pool
            futures.append(
                executor.submit(process_file, file_path, testing, allow_generation, sorted_dir)
            )
            print(f"[+] Queued: {os.path.basename(file_path)}")

        # Wait for all to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # raise exceptions if any occurred in the thread
            except Exception as e:
                print(f"[!] Error in thread: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()

    print(f"\n All files processed in {time.time() - start_time:.2f}s\n")

