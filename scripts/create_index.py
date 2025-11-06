import time
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import argparse

parser = argparse.ArgumentParser(description="Create FAISS index for folder labels.")
parser.add_argument("--model", type=str, default="all-mpnet-base-v2", help="SentenceTransformer model name to use for embeddings.")
args = parser.parse_args()
MODEL_NAME = args.model
# --------- Config ---------
FAISS_INDEX_FILE = "./folder_embeddings.faiss"
LABELS_FILE = "./folder_labels.json"

def create_faiss_index():
    try:
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            folder_data = json.load(f)

        FOLDER_LABELS = list(folder_data.keys())
        FOLDER_DESC = list(folder_data.values())
        extra_examples = {
        "Physics": "Keywords: velocity, prism, ohm, current, resistance, focal length, refraction",
        "Mathematics": "Keywords: calculus, differentiation, trigonometry, probability, matrix",
        "Chemistry": "Keywords: titration, molarity, acid-base, kinetics, organic, inorganic",
        "Informatic Practices": "Keywords: python, pandas, matplotlib, sql, database, csv",
        "English": "Keywords: essay, poem, grammar, literature, asl, comprehension",
        "Official Document": "Keywords: certificate, resume, transcript, letter, contract",
    }
        for label in folder_data:
            folder_data[label] += " " + extra_examples.get(label, "")

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
    except Exception as e:
        print(f"[!] Error creating FAISS index: {e}")

if __name__ == "__main__":
    print("You can change the folder labels and descriptions in 'folder_labels.json' before running this script.")
    print("To change model use the argument --model <MODEL_NAME>, default is set to 'all-mpnet-base-v2'.")
    print("Creating FAISS index with model :", MODEL_NAME)
    create_faiss_index()