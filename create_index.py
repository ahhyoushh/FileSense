import time
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json

# --------- Config ---------
FAISS_INDEX_FILE = "folder_embeddings.faiss"
LABELS_FILE = "folder_labels.json"
MODEL_NAME = "all-MiniLM-L6-v2"    # You can change to any SentenceTransformer model


def create_faiss_index():
    with open(LABELS_FILE, "r", encoding="utf-8") as f:
        folder_data = json.load(f)

    FOLDER_LABELS = list(folder_data.keys())
    FOLDER_DESC = list(folder_data.values())
    combined_desc = [f"{label} {desc}" for label, desc in zip(FOLDER_LABELS, FOLDER_DESC)]
    print(f'Found {len(FOLDER_LABELS)} folder labels for indexing.')

    #Load model and encode
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    print("Generating Embeddings with {MODEL_NAME} model...")
    start = time.time()
    folder_embeddings = model.encode(combined_desc, normalize_embeddings=True, show_progress_bar=True).astype(np.float32)
    folder_embeddings = folder_embeddings / np.linalg.norm(folder_embeddings, axis=1, keepdims=True)

    end = time.time()
    print(f'Embeddings generated in {end - start:.2f} seconds.')

    print("Creating FAISS index...")
    dimension = folder_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # using dot product for cosine similarity
    index.add(folder_embeddings)


    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(LABELS_FILE, "w", encoding="utf-8") as f:
        json.dump(folder_data, f, indent=2)

    print(f"✅ FAISS index saved to {FAISS_INDEX_FILE} for labels: {FOLDER_LABELS}")

if __name__ == "__main__":
    create_faiss_index()