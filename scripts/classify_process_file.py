import os
import re
import shutil
import json
import time
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from create_index import MODEL_NAME
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
# CLASSIFIER 
# -----------------------
def classify_file(text, filename):
    """
    Classifies a file using both its text content and its filename for context.
    """
    clean_filename = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
    
    combined_input = f"{clean_filename}\n\n{text}"
    text_clean = re.sub(r"\s+", " ", combined_input.strip().lower())

    text_emb = model.encode([text_clean])[0]
    folder_embs = model.encode(FOLDER_DESC)

    sims = np.dot(folder_embs, text_emb) / (
        np.linalg.norm(folder_embs, axis=1) * np.linalg.norm(text_emb)
    )

    keyword_map = {
        "physics": ["physics", "experiment", "newton", "motion", "electric field", "ohm", "lab", "ray", "optics", "refraction", "reflection", "lens", "prism"],
        "chemistry": ["chemistry", "reaction", "acid", "base", "salt", "titration", "molecule", "investigatory"],
        "informatic practices": ["python", "program", "csv", "database", "pandas", "sql", "ip", "informat", "practical"],
        "english": ["essay", "literature", "story", "poem", "writing", "english", "play", "report", "project work"],
        "math": ["math", "algebra", "geometry", "calculus", "function", "equation"],
    }

    boosted = sims.copy()
    filename_lower = filename.lower()

    FILENAME_BOOST = 0.2 # High priority boost for keywords in filename
    for i, label in enumerate(FOLDER_LABELS):
        if re.search(rf"\b{re.escape(label.lower())}\b", filename_lower):
            boosted[i] += FILENAME_BOOST
            continue # Apply boost once and move to the next label
        for kw in keyword_map.get(label.lower(), []):
            if re.search(rf"\b{re.escape(kw)}\b", filename_lower):
                boosted[i] += FILENAME_BOOST
                break 

    TEXT_BOOST = 0.1 #Lower priority boost for keywords in text content
    for i, label in enumerate(FOLDER_LABELS):
        for kw in keyword_map.get(label.lower(), []):
            if re.search(rf"\b{re.escape(kw)}\b", text_clean):
                boosted[i] += TEXT_BOOST
                break

    best_idx = int(np.argmax(boosted))
    best_label = FOLDER_LABELS[best_idx]
    best_sim = boosted[best_idx]

    if best_sim >= THRESHOLD:
        return best_label, round(float(best_sim), 2)

    return "Unsorted", round(float(best_sim), 2)


def process_file(file_path, testing=False):
    start_time = time.time()
    filename = os.path.basename(file_path)
    text = extract_text(file_path)

    if not text.strip() or text == filename: #If fails use filename as fallback
        print(f"No readable text in {filename} — relying on filename for classification.")
        text = filename.replace("_", " ").replace("-", " ")

    predicted_folder, similarity = classify_file(text, filename)

    destination_folder = BASE_DIR / "sorted" / predicted_folder
    os.makedirs(destination_folder, exist_ok=True)
    if not testing:
        try:
            shutil.move(file_path, os.path.join(destination_folder, filename))
        except Exception as e:
            print(f"Error moving file {file_path} -> {predicted_folder}: {e}")

    time_taken = time.time() - start_time
    print(f"{filename} -> {predicted_folder} (sim={similarity:.2f}) in {time_taken:.2f} seconds")