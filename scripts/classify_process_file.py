import os
import re
import shutil
import json
import time
from pathlib import Path
import threading

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from generate_label import generate_folder_label
from create_index import create_faiss_index, MODEL_NAME
from extract_text import extract_text

BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_INDEX_FILE = BASE_DIR / "folder_embeddings.faiss"
LABELS_FILE = BASE_DIR / "folder_labels.json"
THRESHOLD = 0.4
low_confidence_threshold = 0.3
index = None
folder_data = {}
FOLDER_LABELS = []
model = None

# Rlock(fun-est experience debugging )
CLASSIFICATION_LOCK = threading.RLock() 

def load_index_and_labels():
    global index, folder_data, FOLDER_LABELS, model 
    try:
        if not FAISS_INDEX_FILE.exists() or not LABELS_FILE.exists():
            print(f"[!] Error: Missing required files...")
            return False
        index = faiss.read_index(str(FAISS_INDEX_FILE))
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            folder_data = json.load(f)
        FOLDER_LABELS = list(folder_data.keys())
        if not FOLDER_LABELS:
            return False
        if model is None: 
            model = SentenceTransformer(MODEL_NAME, device="cpu")
        return True
    except Exception as e:
        print(f"[!] An error occurred while loading index or labels: {e}")
        return False

def classify_file(text, filename, allow_generation=True, TRAIN=False):
    if not index or not model:
        return "Uncategorized", 0.0

    # Local copies to avoid UnboundLocalError when modifying them
    current_threshold = THRESHOLD
    current_low_threshold = low_confidence_threshold

    clean_filename = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
    combined_input = f"{clean_filename}\n\n{text}"
    text_clean = re.sub(r"\s+", " ", combined_input.strip().lower())
    text_emb = model.encode([text_clean], normalize_embeddings=True)
    D, I = index.search(text_emb, 10)
    
    all_sims = np.zeros(len(FOLDER_LABELS), dtype=np.float32)
    for i in range(len(I[0])):
        idx, sim = I[0][i], D[0][i]
        if idx != -1:
            all_sims[idx] = sim

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
                boosted[i] += TEXT_BOOST
                break

    best_idx = int(np.argmax(boosted))
    best_label, best_sim = FOLDER_LABELS[best_idx], boosted[best_idx]

    if best_sim >= current_threshold:
        return best_label, round(float(best_sim), 2)
    else:
        if not allow_generation:
            decrease_amount = 0.07
            current_threshold = current_threshold - decrease_amount
            current_low_threshold = current_low_threshold - decrease_amount
            
            if best_sim > current_low_threshold:
                print(f"[!] [NO GEN] Low confidence ({best_sim:.2f}) but accepting '{best_label}' as fallback.")
                return best_label, round(float(best_sim), 2)
                
        if allow_generation:
            with CLASSIFICATION_LOCK:
                # Another thread might have updated the index while we were waiting for the lock.
                retry_label, retry_sim = classify_file(
                    text, filename, allow_generation=False, TRAIN=TRAIN
                )
                
                # Use global THRESHOLD here to ensure we don't skip based on lowered standards
                if retry_sim >= THRESHOLD:
                    print(f"[!] Index updated by another thread. '{filename}' matched to '{retry_label}' ({retry_sim:.2f}). Skipping generation.")
                    return retry_label, retry_sim

                print(f"[?] Low confidence ({best_sim:.2f}) for '{filename}'. Generating label...")
                new_label_info = generate_folder_label(text)
                
                if new_label_info and new_label_info.get("folder_label"):
                    if create_faiss_index():
                        load_index_and_labels()
                        if TRAIN == True:
                            print(f"[+] [TRAIN MODE] Re-classified '{filename}' again until not Categorised")
                            return classify_file(
                                text, filename, allow_generation=True, TRAIN=TRAIN
                            )

                return classify_file(
                    text, filename, allow_generation=False, TRAIN=TRAIN
                )
        else:
            if best_sim > current_low_threshold:
                print(f"[!] Low confidence ({best_sim:.2f}) but accepting '{best_label}' as fallback.")
                return best_label, round(float(best_sim), 2)
            
            print(f"[!] Could not classify '{filename}' (Sim: {best_sim:.2f}). Moving to Uncategorized or generating Label.")
            return "Uncategorized", 0.0

def process_file(file_path, testing=False, allow_generation=True, TRAIN=False):
    start_time = time.time()
    filename = os.path.basename(file_path)
    text = extract_text(file_path)

    if not text.strip() or text == filename:
        text = filename.replace("_", " ").replace("-", " ")

    predicted_folder, similarity = classify_file(
        text, filename, allow_generation=allow_generation, TRAIN=TRAIN
    )
    
    destination_folder = BASE_DIR / "sorted" / predicted_folder
    os.makedirs(destination_folder, exist_ok=True)
    
    if not testing:
        try:
            shutil.move(file_path, destination_folder / filename)
        except Exception as e:
            print(f"Error moving file {file_path} -> {predicted_folder}: {e}")

    time_taken = time.time() - start_time
    print(f"[1] Processed: {filename} -> {predicted_folder} (sim={similarity:.2f}) in {time_taken:.2f}s")
