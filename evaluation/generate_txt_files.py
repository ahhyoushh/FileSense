import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "files")
TEST_OUTPUT_DIR = os.path.join(BASE_DIR, "..", "test_files")

NUM_FILES = 50
TRAIN_SPLIT = 0.2*NUM_FILES #USED TO GEN LABELS
TEST_SPLIT = 0.8*NUM_FILES
def generate_text_files(data: list):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        for i in range(NUM_FILES):
            text = data[i]["text"]

            filename = f"file_{i+1:03d}.txt"
            if i < TRAIN_SPLIT:
                filename = "train_" + filename
                filepath = os.path.join(OUTPUT_DIR, filename)
            else:
                filename = "test_" + filename
                filepath = os.path.join(TEST_OUTPUT_DIR, filename)
                os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
        print(f"Generated {TRAIN_SPLIT} text files in '{OUTPUT_DIR}' and {TEST_SPLIT} in '{TEST_OUTPUT_DIR}'")