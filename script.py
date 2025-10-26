import os, shutil, json, faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from create_index import FAISS_INDEX_FILE, LABELS_FILE, MODEL_NAME

# Config
files_dir = "files"
THRESHOLD = 0.3 # Similarity threshold

index = faiss.read_index(FAISS_INDEX_FILE)
with open(LABELS_FILE, "r", encoding="utf-8") as f:
    folder_data = json.load(f)

FOLDER_LABELS = list(folder_data.keys())

model = SentenceTransformer(MODEL_NAME, device="cpu")


# Text extraction
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        import PyPDF2
        reader = PyPDF2.PdfReader(file_path)
        return " ".join([page.extract_text() for page in reader.pages])
    elif file_path.endswith(".docx"):
        import docx
        doc = docx.Document(file_path)
        return " ".join([p.text for p in doc.paragraphs])
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return os.path.basename(file_path)


# Compute and predict folder

def process_file(file_path):
    text = extract_text(file_path)
    
    combined_text = [f"{file_path} {text}"]

    file_embedding = model.encode(combined_text).astype("float32")
    file_embedding = file_embedding / np.linalg.norm(file_embedding)  # normalize

    # Search nearest folder embedding
    D, I = index.search(file_embedding.reshape(1, -1), k=1)
    nearest_idx = I[0][0]
    similarity = D[0][0]  # IP value, higher = more similar

    if similarity >= THRESHOLD:
        predicted_folder = FOLDER_LABELS[nearest_idx]
    else:
        predicted_folder = "Unsorted"

    os.makedirs(predicted_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(predicted_folder, os.path.basename(file_path)))
    print(f"{os.path.basename(file_path)} -> {predicted_folder} (sim={similarity:.2f})")


files = [os.path.join(files_dir, f) for f in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir, f))]
for file_path in files:
    process_file(file_path)