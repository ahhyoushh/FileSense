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

# Rlock for thread safety - was fun to debug
CLASSIFICATION_LOCK = threading.RLock() 

def load_index_and_labels():
    global index, folder_data, FOLDER_LABELS, model 
    try:
        if model is None: 
            model = SentenceTransformer(MODEL_NAME, device="cpu")

        if not FAISS_INDEX_FILE.exists() or not LABELS_FILE.exists():
            print(f"[!] Warning: Index or Labels file missing. Starting with empty knowledge.")
            folder_data = {}
            FOLDER_LABELS = []
            index = None
            return True

        index = faiss.read_index(str(FAISS_INDEX_FILE))
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            folder_data = json.load(f)
        FOLDER_LABELS = list(folder_data.keys())
        return True
    except Exception as e:
        print(f"[!] An error occurred while loading index or labels: {e}")
        return False

def classify_file(text, filename, allow_generation=True, retries=0):
    # --- SAFETY NET: MAX RETRIES ---
    MAX_RETRIES = 3

    if retries >= MAX_RETRIES:
        print(f"[!] Max retries reached for '{filename}'.")
        print("Please manually input the folder label for this file.")
        manual_label = input(f"Enter label for '{filename}': ").strip()
        
        while not manual_label:
            print("Label cannot be empty.")
            manual_label = input(f"Enter label for '{filename}': ").strip()

        gen_desc = input("Generate description for this label? (y/n): ").strip().lower()

        if gen_desc == 'y':
            print(f"Generating description for '{manual_label}'...")
            with CLASSIFICATION_LOCK:
                new_label_info = generate_folder_label(text, forced_label=manual_label)
                
                if new_label_info and new_label_info.get("folder_label"):
                     if create_faiss_index():
                        load_index_and_labels()
                        return manual_label, 1.0
                
                print("[!] Failed to generate description. Adding label without description.")
        

        print(f"Adding '{manual_label}' to folder labels without description (not indexed yet).")
        
        current_labels = {}
        if LABELS_FILE.exists():
            try:
                with open(LABELS_FILE, "r", encoding="utf-8") as f:
                    current_labels = json.load(f)
            except Exception:
                current_labels = {}
        
        if manual_label not in current_labels:
            current_labels[manual_label] = f"{manual_label} Keywords: "
            with open(LABELS_FILE, "w", encoding="utf-8") as f:
                json.dump(current_labels, f, indent=2)
        

        return manual_label, 1.0

    if not model:
        load_index_and_labels()
        if not model:
            return "Uncategorized", 0.0

    current_threshold = THRESHOLD
    current_low_threshold = low_confidence_threshold

    best_label = "Uncategorized"
    best_sim = 0.0

    if index and FOLDER_LABELS:
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
            current_threshold -= decrease_amount
            current_low_threshold -= decrease_amount
            
            if best_sim > current_low_threshold:
                if retries > 0:
                    print(f"[!] [RETRY SUCCESS] '{filename}' matched '{best_label}' ({best_sim:.2f}) after update.")
                else:
                    print(f"[!] [NO GEN] Low confidence ({best_sim:.2f}) but accepting '{best_label}' as fallback.")
                return best_label, round(float(best_sim), 2)
            else:
                return "Uncategorized", 0.0
                
        if allow_generation:
            with CLASSIFICATION_LOCK:
                if index:
                    retry_label, retry_sim = classify_file(
                        text, filename, allow_generation=False, retries=retries
                    )
                    if retry_label != "Uncategorized":
                        return retry_label, retry_sim

                print(f"[?] Low confidence ({best_sim:.2f}) for '{filename}'. Generating label (Attempt {retries+1})...")
                new_label_info = generate_folder_label(text)
                
                if new_label_info and new_label_info.get("folder_label"):
                    if create_faiss_index():
                        load_index_and_labels() 
                        print(f"[1] [ONE-SHOT] Re-checking '{filename}'...")
                        return classify_file(
                            text, filename, allow_generation=allow_generation, retries=retries+1
                        )

                return classify_file(
                    text, filename, allow_generation=False, retries=retries
                )

def process_file(file_path, testing=False, allow_generation=True):
    start_time = time.time()
    filename = os.path.basename(file_path)
    
    text = extract_text(file_path, fallback=False)

    if not text.strip() or text == filename:
        text = filename.replace("_", " ").replace("-", " ")

    predicted_folder, similarity = classify_file(
        text, filename, allow_generation=False
    )


    if (predicted_folder == "Uncategorized" or similarity < 0.35) and os.path.exists(file_path):
        print(f"[!] Low confidence ({similarity:.2f}) on first pass. Attempting Fallback Extraction...")
        
        fallback_text = extract_text(file_path, fallback=True)
        
        if fallback_text and len(fallback_text) > 50 and fallback_text != text:
             new_folder, new_sim = classify_file(
                fallback_text, filename, allow_generation=False
             )
             
             if new_sim > similarity:
                 print(f"   -> Fallback improved result: {new_folder} ({new_sim:.2f})")
                 text = fallback_text
                 predicted_folder = new_folder
                 similarity = new_sim
             else:
                 print(f"   -> Fallback did not improve result.")


    if allow_generation and (predicted_folder == "Uncategorized" or similarity < THRESHOLD):
        predicted_folder, similarity = classify_file(
            text, filename, allow_generation=True
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