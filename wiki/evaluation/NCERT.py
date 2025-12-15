import os
import shutil
import random

# how many files per prefix/category
N_PER_CATEGORY = 2   # set to 1 if you want exactly one per acc/physics/etc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# NCERT/dataset/*.md  (one level up from evaluation/)
SOURCE_DIR = os.path.abspath(os.path.join(BASE_DIR,"datasets" ,"NCERT_DATA"))

# files/ (also one level up from evaluation/)
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "files"))

print("BASE_DIR:", BASE_DIR)
print("SOURCE_DIR:", SOURCE_DIR)
print("OUTPUT_DIR:", OUTPUT_DIR)
print("SOURCE_DIR exists?", os.path.isdir(SOURCE_DIR))

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.isdir(SOURCE_DIR):
    raise SystemExit("SOURCE_DIR does not exist. Fix the path in the script.")

# 1) collect all .md files in NCERT/dataset
all_md = [
    f for f in os.listdir(SOURCE_DIR)
    if f.lower().endswith(".md")
]

print("Total .md files found:", len(all_md))

# 2) group by prefix before first "_"
from collections import defaultdict
groups = defaultdict(list)

for fname in all_md:
    base = os.path.splitext(fname)[0]  # remove .md
    prefix = base.split("_")[0]       # 'acc_11_1.md' -> 'acc'
    full_path = os.path.join(SOURCE_DIR, fname)
    groups[prefix].append(full_path)

print("Detected prefixes/categories:", list(groups.keys()))

# 3) copy N_PER_CATEGORY from each prefix into files/
total_copied = 0

for prefix, files_for_prefix in groups.items():
    if not files_for_prefix:
        continue

    # choose up to N_PER_CATEGORY random files from this prefix
    k = min(N_PER_CATEGORY, len(files_for_prefix))
    selected = random.sample(files_for_prefix, k)

    for src in selected:
        src_name = os.path.basename(src)
        # optional: prefix again to be super safe / readable
        dest_name = f"{prefix}__{src_name}"
        dest_path = os.path.join(OUTPUT_DIR, dest_name)
        shutil.copy2(src, dest_path)
        print(f"[{prefix}] copied {src} -> {dest_path}")
        total_copied += 1

print(f"\nDone. Copied {total_copied} files into {OUTPUT_DIR}")
