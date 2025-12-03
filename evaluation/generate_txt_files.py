# generate_txt_files.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "files")
TEST_OUTPUT_DIR = os.path.join(BASE_DIR, "..", "test_files")


def generate_text_files(train_data: list, test_data: list):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

    # train files
    for i, item in enumerate(train_data):
        text = item["text"]
        filename = f"train_file_{i + 1:03d}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

    # test files
    for i, item in enumerate(test_data):
        text = item["text"]
        filename = f"test_file_{i + 1:03d}.txt"
        filepath = os.path.join(TEST_OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

    print(
        f"Generated {len(train_data)} train files in '{OUTPUT_DIR}' "
        f"and {len(test_data)} test files in '{TEST_OUTPUT_DIR}'"
    )
