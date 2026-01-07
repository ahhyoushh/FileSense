import os
import argparse
import sys
from pathlib import Path

# Add project root so imports work even when running directly
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Environment configuration for thread-safe execution with ML libraries
os.environ.update({
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "TOKENIZERS_PARALLELISM": "false"
})


from multhread import process_multiple
from classify_process_file import process_file, load_index_and_labels 
from scripts.logger.logger import setup_logger, get_logger, restore_stdout


parser = argparse.ArgumentParser(description="Process files in a directory concurrently.")
parser.add_argument("--dir", "-d", type=str, default="./files", help="Folder to organise.")
parser.add_argument("--threads", "-t", type=int, default=6, help="Maximum number of concurrent threads.")
parser.add_argument("--single-thread", action="store_true", help="Run in single-threaded mode instead of multi-threaded.")
parser.add_argument("--no-generation", action="store_true", help="Do not allow generation if classification fails.")
parser.add_argument("--test", action="store_true", help="Run in testing mode (no file moves).")
parser.add_argument("--sorted-dir", type=str, default=None, help="Directory to move sorted files into.")
parser.add_argument("--auto-save-logs", action="store_true", help="Automatically save logs without prompting.")
parser.add_argument("--no-logs", action="store_true", help="Disable logging for this run.")
parser.add_argument("--model", type=str, default="BAAI/bge-base-en-v1.5", help="Embedding model to use.")
parser.add_argument("--disable-rl", action="store_true", default=True, help="Disable RL features and uploads (default: True).")
parser.add_argument("--enable-rl", action="store_false", dest="disable_rl", help="Enable RL features and uploads.")
args = parser.parse_args()

def prompt_save_logs(logger):
    restore_stdout()
    try:
        print("\n" + "="*60)
        response = input("Save logs from this run? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            custom_name = input("Enter custom log filename (or press Enter for timestamp): ").strip()
            if custom_name and not custom_name.endswith('.log'):
                custom_name += '.log'
            log_path = logger.save_logs(custom_name) if custom_name else logger.save_logs()
            print(f"[OK] Logs saved to: {log_path}")
        else:
            print("Logs not saved.")
        print("="*60)
    except Exception as e:
        print(f"Error while saving logs: {e}")

if __name__ == "__main__":
    logger = None
    testing = args.test

    from classify_process_file import set_rl_disabled, start_rl_sync
    set_rl_disabled(args.disable_rl)
    start_rl_sync()

    if not args.no_logs:
        logger = setup_logger()
        print("Logging initialized. Capturing stdout.\n")
    
    try:
        # Set Model Config first
        from scripts.create_index import set_model_config
        set_model_config(args.model)

        if not load_index_and_labels():
            print("\n[!] Initialization failed. Cannot start processing.")
            sys.exit(1)

        files_dir = args.dir
        MAX_THREADS = args.threads

        if not os.path.isdir(files_dir):
            print(f"Error: Directory not found: '{files_dir}'")
            sys.exit(1)

        if args.single_thread:
            print(f"Processing files in SINGLE-THREADED mode: {files_dir}")
            files = [
                os.path.join(files_dir, f)
                for f in os.listdir(files_dir)
                if os.path.isfile(os.path.join(files_dir, f))
            ]
            if not files:
                print("No files found.")
            else:
                for file_path in files:
                    process_file(file_path, testing=testing, allow_generation=not args.no_generation, sorted_dir=args.sorted_dir)

        else:
            print(f"Processing with {MAX_THREADS} threads.")
            process_multiple(
                files_dir,
                MAX_THREADS,
                testing=testing,
                allow_generation=not args.no_generation,
                sorted_dir=args.sorted_dir
            )

    finally:
        if logger and not args.no_logs:
            if args.auto_save_logs:
                log_path = logger.save_logs()
                restore_stdout()
                print(f"\n[OK] Logs auto-saved to: {log_path}")
            else:
                prompt_save_logs(logger)
