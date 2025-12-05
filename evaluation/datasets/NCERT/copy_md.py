import os
import shutil
import glob

# run this from the NCERT directory (the one you showed)
print("CWD:", os.getcwd())
print("Contains:", os.listdir("."))

SOURCE_DIR = "ncert-all"
DEST_DIR = "dataset"

if not os.path.isdir(SOURCE_DIR):
    raise SystemExit(f"Source dir not found: {SOURCE_DIR}")

os.makedirs(DEST_DIR, exist_ok=True)

# find all markdown-like files (case-insensitive)
patterns = [
    os.path.join(SOURCE_DIR, "**", "*.md"),
    os.path.join(SOURCE_DIR, "**", "*.MD"),
]
md_files = []
for pattern in patterns:
    md_files.extend(glob.glob(pattern, recursive=True))

# dedupe
md_files = sorted(set(md_files))

print(f"Found {len(md_files)} .md/.MD files under {SOURCE_DIR}")

count = 0
for src_path in md_files:
    # build flat unique name based on relative path
    rel_path = os.path.relpath(src_path, SOURCE_DIR)
    safe_name = rel_path.replace(os.sep, "_")  # acc_11_1/acc_11_1.md -> acc_11_1_acc_11_1.md
    dest_path = os.path.join(DEST_DIR, safe_name)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src_path, dest_path)
    print(f"Copied: {src_path} -> {dest_path}")
    count += 1

print(f"\nCopied {count} markdown files to {DEST_DIR}")
