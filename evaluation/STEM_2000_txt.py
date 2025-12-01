import csv
import random
from generate_txt_files import generate_text_files

CSV_PATH = 'evaluation/datasets/STEM.csv'

def main():
    data = []
    
    # Load CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get("text")
            if not text:
                continue
            data.append({"text": str(text)})

    # Correct shuffle (in-place, DO NOT assign)
    random.shuffle(data)

    print("Generating text files...")
    generate_text_files(data)

main()
