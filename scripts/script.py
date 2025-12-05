import os
import argparse
import sys
from multhread import process_multiple
from classify_process_file import process_file, load_index_and_labels 
from train import train
from logger import setup_logger, get_logger, restore_stdout

test = True
parser = argparse.ArgumentParser(description="Process files in a directory concurrently.")
parser.add_argument("--dir", "-d", type=str, default="./files", help="Folder to organise.")
parser.add_argument("--threads", "-t", type=int, default=6, help="Maximum number of concurrent threads.")
parser.add_argument("--single-thread", action="store_true", help="Run in single-threaded mode instead of multi-threaded.")
parser.add_argument("--no-generation", action="store_true", help="Do not allow generation if classification fails.")
parser.add_argument("--train", action="store_true", help="Enable training mode during processing.")
parser.add_argument("--auto-save-logs", action="store_true", help="Automatically save logs without prompting.")
parser.add_argument("--no-logs", action="store_true", help="Disable logging for this run.")
args = parser.parse_args()

def prompt_save_logs(logger):
    """Ask user if they want to save the logs from this run"""
    restore_stdout()  # Temporarily restore stdout for clean user input
    
    try:
        print("\n" + "="*60)
        response = input("Would you like to save the logs from this run? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            custom_name = input("Enter custom log filename (or press Enter for timestamp): ").strip()
            
            if custom_name:
                if not custom_name.endswith('.log'):
                    custom_name += '.log'
                log_path = logger.save_logs(custom_name)
            else:
                log_path = logger.save_logs()
            
            if log_path:
                print(f"✓ Logs saved to: {log_path}")
            else:
                print("✗ Failed to save logs.")
        else:
            print("Logs not saved.")
        print("="*60)
    except KeyboardInterrupt:
        print("\nLog save cancelled.")
    except Exception as e:
        print(f"Error during log save prompt: {e}")

if __name__ == "__main__":
    # Setup logging unless disabled
    logger = None
    if not args.no_logs:
        logger = setup_logger()
        print("[*] Logging enabled. All output will be captured.\n")
    
    try:
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
                    if args.train:
                        train(files_dir, testing=test)
                    else:
                        process_file(file_path, testing=test, allow_generation=not args.no_generation)
        else:
            if args.train:
                train(files_dir, testing=test)
            else:             
                print(f"Processing files in directory: {files_dir} with {MAX_THREADS} threads.")
                process_multiple(files_dir, MAX_THREADS, testing=test, allow_generation=not args.no_generation)
    
    finally:
        # After execution, handle log saving
        if logger and not args.no_logs:
            if args.auto_save_logs:
                log_path = logger.save_logs()
                restore_stdout()
                if log_path:
                    print(f"\n✓ Logs automatically saved to: {log_path}")
            else:
                prompt_save_logs(logger)
