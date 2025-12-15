import csv
import random
from pathlib import Path
from generate_txt_files import generate_text_files

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / 'datasets' / 'STEM.csv'

# How many text files you want to generate
NUM_FILES = 50  # <- change as needed

def main():
    data = []

    # Load CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get("text")
            if text:
                data.append({"text": str(text)})

    # Shuffle
    random.shuffle(data)

    # Slice only the amount you want
    selected_data = data[:NUM_FILES]

    print(f"Generating {len(selected_data)} files...")
    generate_text_files(selected_data)

main()
