# main.py
# AG = Andrew G, the author lamao
from datasets import load_dataset
from collections import defaultdict
import random

from generate_txt_files import generate_text_files

NUM_FILES = 100
TRAIN_RATIO = 0.2  # 20% train, 80% test


def stratified_sample(data, num_files, train_ratio=0.2):
    """
    Returns (train, test) lists of length ~ num_files,
    guaranteeing every label appears in both splits.
    """
    buckets = defaultdict(list)
    for item in data:
        buckets[item["label"]].append(item)

    # shuffle items per label for randomness
    for label in buckets:
        random.shuffle(buckets[label])

    train_size = int(num_files * train_ratio)
    test_size = num_files - train_size

    train = []
    test = []

    # STEP 1: guarantee each label in both splits
    for label, items in buckets.items():
        if len(items) < 2:
            raise ValueError(
                f"Label {label} has less than 2 samples; "
                "cannot guarantee presence in both train and test."
            )
        train.append(items.pop())
        test.append(items.pop())

    # STEP 2: fill remaining slots from leftover pool
    remaining = []
    for items in buckets.values():
        remaining.extend(items)

    random.shuffle(remaining)

    need_train = max(0, train_size - len(train))
    need_test = max(0, test_size - len(test))

    train.extend(remaining[:need_train])
    test.extend(remaining[need_train:need_train + need_test])

    # If not enough data, you'll get shorter splits – that’s fine or you can assert here.
    return train, test


def main():
    print("Loading AG News dataset...")
    ds = load_dataset("ag_news", split="train")
    data = list(ds)

    # (optional) global shuffle, not strictly needed
    random.shuffle(data)

    train, test = stratified_sample(data, NUM_FILES, train_ratio=TRAIN_RATIO)

    generate_text_files(train, test)


if __name__ == "__main__":
    main()
