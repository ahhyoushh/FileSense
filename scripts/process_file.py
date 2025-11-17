import os
import shutil
import json
import faiss
import re
import time
from sentence_transformers import SentenceTransformer
import numpy as np
from create_index import MODEL_NAME
from pathlib import Path
from extract_text import extract_text
BASE_DIR = Path(__file__).resolve().parent.parent  # main FileSense folder
FAISS_INDEX_FILE = BASE_DIR / "folder_embeddings.faiss"
LABELS_FILE = BASE_DIR / "folder_labels.json"

THRESHOLD = 0.45  

index = faiss.read_index(str(FAISS_INDEX_FILE))
with open(LABELS_FILE, "r", encoding="utf-8") as f:
    folder_data = json.load(f)

FOLDER_LABELS = list(folder_data.keys())
FOLDER_DESC = list(folder_data.values())
model = SentenceTransformer(MODEL_NAME, device="cpu")

# -----------------------
# CLASSIFIER (unchanged mostly)
# -----------------------
def classify_file(text):
    import re

    text_clean = re.sub(r"\s+", " ", text.strip().lower())

    # gen embeddings
    text_emb = model.encode([text_clean])[0]
    folder_embs = model.encode(FOLDER_DESC)

    sims = np.dot(folder_embs, text_emb) / (
        np.linalg.norm(folder_embs, axis=1) * np.linalg.norm(text_emb)
    )

    keyword_map = {
        "physics": ["physics", "experiment", "newton", "motion", "electric field", "ohm", "lab", "ray", "optics", "refraction", "reflection", "lens", "prism"],
        "chemistry": ["chemistry", "reaction", "acid", "base", "salt", "titration", "molecule"],
        "informatic practices": ["python", "program", "csv", "database", "pandas", "sql", "ip", "informat"],
        "english": ["essay", "literature", "story", "poem", "writing", "english", "play", "report"],
        "math": ["math", "algebra", "geometry", "calculus", "function", "equation"],
    }

    # boost similarity if keywords found
    boosted = sims.copy()
    for i, label in enumerate(FOLDER_LABELS):
        for kw in keyword_map.get(label.lower(), []):
            if re.search(rf"\b{re.escape(kw)}\b", text_clean):
                boosted[i] += 0.1
                break

    best_idx = int(np.argmax(boosted))
    best_label = FOLDER_LABELS[best_idx]
    best_sim = boosted[best_idx]

    if best_sim >= THRESHOLD:
        return best_label, round(float(best_sim), 2)

    # fallback: if any keyword_map matches independent of similarity, return that label
    for label, kws in keyword_map.items():
        for kw in kws:
            if re.search(rf"\b{re.escape(kw)}\b", text_clean):
                return label.title(), round(float(best_sim), 2)

    return "Unsorted", round(float(best_sim), 2)


def process_file(file_path):
    start_time = time.time()
    text = extract_text(file_path)
    if not text.strip():
        print(f"No readable text in {os.path.basename(file_path)} — skipping semantic match.")
        text = os.path.basename(file_path)

    predicted_folder, similarity = classify_file(text)

    os.makedirs(BASE_DIR / "sorted" / predicted_folder, exist_ok=True)
    try:
        shutil.move(file_path, os.path.join(BASE_DIR / "sorted" / predicted_folder, os.path.basename(file_path)))
    except Exception as e:
        print(f"Error moving file {file_path} -> {predicted_folder}: {e}")

    time_taken = time.time() - start_time

    print(f"{os.path.basename(file_path)} -> {predicted_folder} (sim={similarity:.2f}) in {time_taken:.2f} seconds")
