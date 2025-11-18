# --- START OF FILE classify_process_file.py ---

import os
import re
import shutil
import json
import time
from pathlib import Path
import threading
import sys

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from generate_label import generate_folder_label
from create_index import create_faiss_index, MODEL_NAME
from extract_text import extract_text

BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_INDEX_FILE = BASE_DIR / "folder_embeddings.faiss"
LABELS_FILE = BASE_DIR / "folder_labels.json"
THRESHOLD = 0.45

index = None
folder_data = {}
FOLDER_LABELS = []
model = None
CLASSIFICATION_LOCK = threading.Lock() 

def load_index_and_labels():
    global index, folder_data, FOLDER_LABELS, model
    print("Loading classification model and index...")
    try:
        if not FAISS_INDEX_FILE.exists() or not LABELS_FILE.exists():
            print(f"[!] Error: Missing required files...")
            return False
        index = faiss.read_index(str(FAISS_INDEX_FILE))
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            folder_data = json.load(f)
        FOLDER_LABELS = list(folder_data.keys())
        if not FOLDER_LABELS:
            print("[!] The labels file is empty. Cannot proceed.")
            return False
        if model is None: 
            model = SentenceTransformer(MODEL_NAME, device="cpu")
        print(f"[1] Loaded {len(FOLDER_LABELS)} labels and index successfully.")
        return True
    except Exception as e:
        print(f"[!] An error occurred while loading index or labels: {e}")
        return False

def classify_file(text, filename):
    if not index or not model:
        return "Uncategorized", 0.0

    clean_filename = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
    combined_input = f"{clean_filename}\n\n{text}"
    text_clean = re.sub(r"\s+", " ", combined_input.strip().lower())
    text_emb = model.encode([text_clean], normalize_embeddings=True)
    D, I = index.search(text_emb, 10)
    
    all_sims = np.zeros(len(FOLDER_LABELS), dtype=np.float32)
    for i in range(len(I[0])):
        idx, sim = I[0][i], D[0][i]
        if idx != -1: all_sims[idx] = sim

    boosted, filename_lower = all_sims.copy(), filename.lower()
    FILENAME_BOOST, TEXT_BOOST = 0.2, 0.1

    for i, label in enumerate(FOLDER_LABELS):
        full_text = folder_data.get(label, "")
        keywords_str = ""
        if " Keywords: " in full_text:
            parts = full_text.split(" Keywords: ", 1)
            keywords_str = parts[1]
        
        keywords = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]
        
        if re.search(rf"\b{re.escape(label.lower())}\b", filename_lower):
            boosted[i] += FILENAME_BOOST
            continue
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", filename_lower):
                boosted[i] += FILENAME_BOOST
                break

    best_idx = int(np.argmax(boosted))
    best_label, best_sim = FOLDER_LABELS[best_idx], boosted[best_idx]

    if best_sim >= THRESHOLD:
        return best_label, round(float(best_sim), 2)
    else:
        with CLASSIFICATION_LOCK:
            new_label_info = generate_folder_label(text)
            if new_label_info and new_label_info.get("folder_label"):
                new_label_name = new_label_info["folder_label"]
                if new_label_name not in FOLDER_LABELS:
                    if create_faiss_index():
                        load_index_and_labels()
                        return new_label_name, 1.0
                else:
                    return classify_file(text, filename)
            return "Uncategorized", 0.0

def process_file(file_path, testing=False):
    start_time = time.time()
    filename = os.path.basename(file_path)
    text = extract_text(file_path)

    if not text.strip() or text == filename:
        text = filename.replace("_", " ").replace("-", " ")

    predicted_folder, similarity = classify_file(text, filename)
    destination_folder = BASE_DIR / "sorted" / predicted_folder
    os.makedirs(destination_folder, exist_ok=True)
    if not testing:
        try:
            shutil.move(file_path, destination_folder / filename)
        except Exception as e:
            print(f"Error moving file {file_path} -> {predicted_folder}: {e}")

    time_taken = time.time() - start_time
    print(f"[1] Processed: {filename} -> {predicted_folder} (sim={similarity:.2f}) in {time_taken:.2f}s")

