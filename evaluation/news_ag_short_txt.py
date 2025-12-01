# AG = Andrew G, the author lamao
from datasets import load_dataset
import random
from generate_txt_files import generate_text_files

def main():
    print("Loading AG News dataset...")
    ds = load_dataset("ag_news", split="train") # Train has more files
    data = list(ds)

    random.shuffle(data)
    generate_text_files(data)
    
main()