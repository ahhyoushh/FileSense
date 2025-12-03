import os
import shutil
import random
from datasets import load_dataset

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR = os.path.join(BASE_DIR, "..", "files")      # Training Data
TEST_DIR = os.path.join(BASE_DIR, "..", "test_files")  # Test Data

# We want exactly 12 training files (3 per category) to ensure coverage
TRAIN_FILES_PER_CATEGORY = 3 
TOTAL_TEST_FILES = 40

# AG News Label Mapping
LABEL_MAP = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}

def main():
    print("Loading AG News dataset...")
    ds = load_dataset("ag_news", split="train")
    
    # 1. Clean old directories to ensure fresh start
    if os.path.exists(TRAIN_DIR): shutil.rmtree(TRAIN_DIR)
    if os.path.exists(TEST_DIR): shutil.rmtree(TEST_DIR)
    os.makedirs(TRAIN_DIR)
    os.makedirs(TEST_DIR)

    # 2. Bucket data by label
    # This allows us to pick specific categories guaranteed
    buckets = {0: [], 1: [], 2: [], 3: []}
    
    # Shuffle entire dataset first
    data_list = list(ds)
    random.shuffle(data_list)

    for item in data_list:
        label = item['label']
        buckets[label].append(item['text'])

    # 3. Generate GUARANTEED BALANCED Training Set
    # We pick exactly 3 files from every category
    print(f"Generating Balanced Training Set ({TRAIN_FILES_PER_CATEGORY * 4} files)...")
    
    train_file_idx = 1
    used_texts = set()

    for label, texts in buckets.items():
        # Grab the first N texts from this specific category
        selected_texts = texts[:TRAIN_FILES_PER_CATEGORY]
        
        for text in selected_texts:
            filename = f"train_file_{train_file_idx:03d}.txt"
            filepath = os.path.join(TRAIN_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            
            used_texts.add(text) # Remember this so we don't put it in test
            print(f"  [{LABEL_MAP[label]}] Saved -> {filename}")
            train_file_idx += 1

    # 4. Generate Random Test Set
    # Now we fill the test folder with whatever is left (randomly)
    print(f"\nGenerating Random Test Set ({TOTAL_TEST_FILES} files)...")
    test_file_idx = 1
    
    for item in data_list:
        if test_file_idx > TOTAL_TEST_FILES:
            break
            
        # Only use if we didn't use it in training
        if item['text'] not in used_texts:
            filename = f"test_file_{test_file_idx:03d}.txt"
            filepath = os.path.join(TEST_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(item['text'])
            test_file_idx += 1

    print(f"\nDone! Generated {train_file_idx-1} Training files and {test_file_idx-1} Test files.")

if __name__ == "__main__":
    main()