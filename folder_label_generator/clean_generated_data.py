# Paste and run in Colab. Adjust IN_PATH if needed.
import os, shutil, json, re
from itertools import islice

IN_PATH = "folder_label_generator\data.jsonl"            # original file
BACKUP_PATH = IN_PATH + ".bak"
CLEAN_PATH = IN_PATH.replace(".jsonl", "_cleaned.jsonl")
FIXED_COMMAS_PATH = IN_PATH.replace(".jsonl", "_fixedcommas.jsonl")
REPORT_LINES = 5   # how many context lines to print around errors

# 0) safety backup
if not os.path.exists(IN_PATH):
    raise FileNotFoundError(f"Input file not found: {IN_PATH}")
shutil.copy2(IN_PATH, BACKUP_PATH)
print("Backup created:", BACKUP_PATH)

# Helper: show a range of lines for quick inspection
def print_range(path, start_line, end_line):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(islice(f, end_line), start=1):
            if i >= start_line:
                print(f"{i:6d} | {line.rstrip()}")

# 1) Quick scan: find first N bad single-line JSONs (if file *is* JSONL)
print("\n--- Quick per-line JSON validation (first failure shown) ---")
bad_lines = []
with open(IN_PATH, "r", encoding="utf-8") as f:
    for i, raw in enumerate(f, start=1):
        s = raw.strip()
        if not s:
            continue
        try:
            json.loads(s)
        except Exception as e:
            bad_lines.append((i, str(e)))
            break

if not bad_lines:
    print("No per-line JSON errors detected (file may be valid JSONL).")
else:
    ln, err = bad_lines[0]
    print(f"Detected JSON error at line {ln}: {err}")
    start = max(1, ln - REPORT_LINES)
    end = ln + REPORT_LINES
    print(f"\nContext (lines {start}..{end}):")
    print_range(IN_PATH, start, end)

# 2) If file contains pretty-printed / multi-line JSON objects, convert them to JSONL.
#    We group lines into JSON objects by matching braces while ignoring braces inside strings.
def iter_json_objects(file_path):
    buf = []
    depth = 0
    in_string = False
    escape = False
    with open(file_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line and not buf:
                continue
            buf.append(line)
            for ch in line:
                if escape:
                    escape = False
                    continue
                if ch == "\\":
                    escape = True
                    continue
                if ch == '"':
                    in_string = not in_string
                if not in_string:
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
            # When depth == 0 we've closed an object
            if depth == 0 and buf:
                yield "\n".join(buf).strip()
                buf = []
    # leftover buffer
    if buf:
        yield "\n".join(buf).strip()

print("\n--- Converting pretty-printed / multi-line JSON -> single-line JSONL (if needed) ---")
count = 0
failed_parse = False
with open(CLEAN_PATH, "w", encoding="utf-8") as out:
    for obj_text in iter_json_objects(IN_PATH):
        if not obj_text:
            continue
        try:
            obj = json.loads(obj_text)  # ensures valid JSON
            out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            count += 1
        except Exception as e:
            print("\nFailed to parse an object during conversion. Showing prefix for debugging:")
            print(obj_text[:1000])
            print("Error:", e)
            failed_parse = True
            break

if failed_parse:
    print("\nConversion failed — original file likely has malformed JSON. See printed object above.")
else:
    print(f"Wrote {count} JSON objects to {CLEAN_PATH}")

# 3) Attempt tolerant "remove trailing commas" fix on the cleaned file (safe attempt).
#    This will write FIXED_COMMAS_PATH; we will validate it afterwards.
print("\n--- Attempting to remove common trailing commas (safe attempt) ---")
def remove_trailing_commas(s):
    # remove trailing commas before } or ]
    return re.sub(r",\s*([}\]])", r"\1", s)

fixed_count = 0
with open(CLEAN_PATH, "r", encoding="utf-8") as fin, open(FIXED_COMMAS_PATH, "w", encoding="utf-8") as fout:
    for line in fin:
        if not line.strip():
            continue
        fixed_line = remove_trailing_commas(line)
        try:
            json.loads(fixed_line)
            fout.write(fixed_line.rstrip("\n") + "\n")
            fixed_count += 1
        except Exception:
            # if removal breaks it, keep original (so nothing destructive happens)
            fout.write(line)
            fixed_count += 1

print("Wrote attempted-fixed file to", FIXED_COMMAS_PATH)

# 4) Final validation: try json.loads for each line in the FIXED_COMMAS_PATH
print("\n--- Final validation of cleaned file (line-by-line) ---")
first_bad = None
with open(FIXED_COMMAS_PATH, "r", encoding="utf-8") as f:
    for i, raw in enumerate(f, start=1):
        s = raw.strip()
        if not s:
            continue
        try:
            json.loads(s)
        except Exception as e:
            first_bad = (i, str(e), s[:300])
            break

if first_bad is None:
    print("All lines parsed successfully. Final cleaned file:", FIXED_COMMAS_PATH)
    # Optional: show counts and a preview
    total = 0
    with open(FIXED_COMMAS_PATH, "r", encoding="utf-8") as f:
        for _ in f:
            total += 1
    print("Total JSON objects:", total)
    print("\nPreview (first 3 entries):")
    with open(FIXED_COMMAS_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if i > 3:
                break
            print(f"{i:3d} |", line.strip()[:400])
else:
    ln, err, preview = first_bad
    print(f"Validation failed at line {ln}: {err}")
    start = max(1, ln - REPORT_LINES)
    end = ln + REPORT_LINES
    print(f"\nContext (lines {start}..{end}):")
    print_range(FIXED_COMMAS_PATH, start, end)
    print("\nPreview of failing line head (300 chars):")
    print(preview)

# 5) (Optional) Try loading via datasets if all good
try:
    if first_bad is None:
        print("\nAttempting to load cleaned file with Hugging Face `datasets` for a quick sanity check...")
        from datasets import load_dataset
        ds = load_dataset("json", data_files=FIXED_COMMAS_PATH, split="train")
        print("datasets loaded. Number of examples:", len(ds))
        print("Example 0 keys:", list(ds[0].keys()) if len(ds) > 0 else "empty")
except Exception as e:
    print("datasets.load_dataset failed:", e)

print("\n--- DONE ---")
print("Original backup:", BACKUP_PATH)
print("Cleaned file to use:", FIXED_COMMAS_PATH)
