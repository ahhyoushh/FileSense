import time
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path

# --- Config ---
BASE_DIR = Path(__file__).resolve().parent.parent 
FAISS_INDEX_FILE = BASE_DIR / "folder_embeddings.faiss"
LABELS_FILE = BASE_DIR / "folder_labels.json"
MODEL_NAME = "all-mpnet-base-v2"

def create_faiss_index():
    try:
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            folder_data = json.load(f)

        FOLDER_LABELS = list(folder_data.keys())
        if not FOLDER_LABELS:
            print("[!] No folder labels found in the JSON file. Cannot create index.")
            return False

        combined_desc = [f"{label}: {full_text}" for label, full_text in folder_data.items()]
        
        print(f'Found {len(FOLDER_LABELS)} folder labels for indexing.')

        model = SentenceTransformer(MODEL_NAME, device="cpu")
        print(f"Generating Embeddings with {MODEL_NAME} model...")
        start = time.time()
        
        folder_embeddings = model.encode(
            combined_desc, normalize_embeddings=True, show_progress_bar=True
        ).astype(np.float32)
        
        end = time.time()
        print(f'Embeddings generated in {end - start:.2f} seconds.')

        print("Creating FAISS index...")
        dimension = folder_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(folder_embeddings)

        faiss.write_index(index, str(FAISS_INDEX_FILE))

        print(f"[1] FAISS index saved to {FAISS_INDEX_FILE}")
        return True
    except FileNotFoundError:
        print(f"[!] Error: The file '{LABELS_FILE}' was not found.")
        return False
    except Exception as e:
        print(f"[!] Error creating FAISS index: {e}")
        return False

if __name__ == "__main__":
    print("Creating FAISS index with model:", MODEL_NAME)
    create_faiss_index()

