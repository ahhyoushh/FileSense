import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "files")

def generate_text_files(data: list):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, item in enumerate(data):
        text = item["text"]
        filename = f"file_{i + 1:03d}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

    print(f"Generated {len(data)} text files in '{OUTPUT_DIR}'")
