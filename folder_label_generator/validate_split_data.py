import json, re, glob, random
from pathlib import Path

# config
MAX_INPUT_CHARS = 1200
OUTPUT_REGEX = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{1,59}$')  # starts alpha, allowed chars
CHUNKS_GLOB = "folder_label_generator/chunks.jsonl"  # change if your chunks named differently
OUT_TRAIN = "folder_label_generator/train.jsonl"
OUT_VAL = "folder_label_generator/val.jsonl"
VAL_RATIO = 0.10

def load_chunks(glob_pat):
    items = []
    for fname in sorted(glob.glob(glob_pat)):
        print("Loading", fname)
        with open(fname, 'r', encoding='utf-8') as fh:
            for line in fh:
                line=line.strip()
                if not line: continue
                try:
                    obj = json.loads(line)
                except Exception as e:
                    print("skip bad json:", e, line[:200])
                    continue
                if "input" not in obj or "output" not in obj:
                    continue
                items.append(obj)
    return items

def clean_item(obj):
    inp = obj["input"].replace("\r\n","\n")[:MAX_INPUT_CHARS].strip()
    out = obj["output"].strip()
    # normalize output to underscores (keeps underscores/dashes if present)
    out = re.sub(r'\s+', '_', out)
    # remove illegal chars from output
    out = re.sub(r'[^A-Za-z0-9_-]', '', out)
    return {"input": inp, "output": out}

def valid_output(s):
    return bool(OUTPUT_REGEX.match(s))

items = load_chunks(CHUNKS_GLOB)
print("Loaded total:", len(items))

# clean & validate
cleaned = []
seen = set()
for it in items:
    c = clean_item(it)
    key = (c["input"][:120], c["output"])  # coarse dedupe key
    if key in seen: continue
    if not valid_output(c["output"]):
        continue
    seen.add(key)
    cleaned.append(c)

print("After cleaning & dedupe:", len(cleaned))

# shuffle & split
random.shuffle(cleaned)
n = len(cleaned)
n_val = max(1, int(n * VAL_RATIO))
n_train = n - n_val
train = cleaned[:n_train]
val = cleaned[n_train:]

print("Train:", len(train), "Val:", len(val))

# write files
with open(OUT_TRAIN, 'w', encoding='utf-8') as f:
    for o in train:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")

with open(OUT_VAL, 'w', encoding='utf-8') as f:
    for o in val:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")

print("Wrote", OUT_TRAIN, "and", OUT_VAL)
