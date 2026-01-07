import os
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import re
import shutil
import json
import time
import threading
import concurrent.futures

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

from generate_label import generate_folder_label
from create_index import create_faiss_index
import scripts.create_index as ci
from extract_text import extract_text

DISABLE_RL = True

def set_rl_disabled(disabled):
    global DISABLE_RL
    DISABLE_RL = disabled
    if not DISABLE_RL:
        print("RL management enabled.")
    else:
        print("RL management disabled.")

# Delay imports or handle them if RL is disabled
try:
    from scripts.RL.rl_supabase import sync_local_to_supabase, upload_event
    from scripts.logger.rl_logger import get_rl_logger
    from scripts.RL.rl_policy import choose_policy
    from scripts.RL.rl_config import POLICIES
except ImportError:
    if not DISABLE_RL:
        print("[!] RL modules not found but RL is enabled.")
    POLICIES = {}


# Startup logic

def _startup_sync():
    try:
        uploaded, failed = sync_local_to_supabase()
        print(f"Data sync: {uploaded} uploaded, {failed} failed.")
    except Exception as e:
        print("Startup sync error:", e)


def _bg_startup():
    time.sleep(1)
    _startup_sync()


def start_rl_sync():
    if not DISABLE_RL:
        threading.Thread(target=_bg_startup, daemon=True).start()


# Configuration

BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_INDEX_FILE = BASE_DIR / "folder_embeddings.faiss"
LABELS_FILE = BASE_DIR / "folder_labels.json"

THRESHOLD = 0.4
LOW_CONFIDENCE_THRESHOLD = 0.3

index = None
folder_data = {}
FOLDER_LABELS = []
model = None

CLASSIFICATION_LOCK = threading.RLock()
UPLOAD_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2)


# Index Management

def load_index_and_labels():
    global index, folder_data, FOLDER_LABELS, model

    try:
        if model is None:
            print("Initializing inference model...")
            model = SentenceTransformer(ci.MODEL_NAME, device="cpu")
            print("Model loaded.")

        if not FAISS_INDEX_FILE.exists() or not LABELS_FILE.exists():
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
        print("[!] Error loading index/labels:", e)
        return False


# Utilities

def _ret(label, sim, retries=0, top3=None, manual=False):
    if top3 is None:
        top3 = [float(sim or 0.0)]
    top3 = (top3 + [0.0, 0.0])[:3]
    return label, float(sim or 0.0), int(retries), [float(x) for x in top3], bool(manual)


# Core Classification

def classify_file(text, filename, allow_generation=True, retries=0, cfg=None):
    MAX_RETRIES = 3

    if retries >= MAX_RETRIES:
        try:
            new_label_info = generate_folder_label(text)
        except Exception:
            new_label_info = None

        if new_label_info and new_label_info.get("folder_label"):
            forced_label = new_label_info["folder_label"].strip()
            with CLASSIFICATION_LOCK:
                labels = {}
                if LABELS_FILE.exists():
                    try:
                        with open(LABELS_FILE, "r", encoding="utf-8") as f:
                            labels = json.load(f)
                    except Exception:
                        labels = {}

                if forced_label not in labels:
                    labels[forced_label] = new_label_info.get("description", "")
                    with open(LABELS_FILE, "w", encoding="utf-8") as f:
                        json.dump(labels, f, indent=2)

                if create_faiss_index():
                    load_index_and_labels()
                    return _ret(forced_label, 1.0, retries, [1.0, 0.0, 0.0], True)

        return _ret("Uncategorized", 0.0, retries, [0.0, 0.0, 0.0], False)

    if model is None:
        load_index_and_labels()
        if model is None:
            return _ret("Uncategorized", 0.0, retries)

    threshold = cfg.get("THRESHOLD", THRESHOLD) if cfg else THRESHOLD
    low_threshold = cfg.get("LOW_CONF", LOW_CONFIDENCE_THRESHOLD) if cfg else LOW_CONFIDENCE_THRESHOLD

    best_label = "Uncategorized"
    best_sim = 0.0
    top3 = [0.0, 0.0, 0.0]

    if index and FOLDER_LABELS:
        clean_filename = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
        combined = f"{clean_filename}\n{text}"
        emb = model.encode([combined], normalize_embeddings=True)

        D, I = index.search(emb, 10)
        sims = np.zeros(len(FOLDER_LABELS), dtype=np.float32)

        for i, idx in enumerate(I[0]):
            if idx != -1:
                sims[idx] = D[0][i]

        sorted_idxs = np.argsort(-sims)
        best_label = FOLDER_LABELS[int(sorted_idxs[0])]
        best_sim = float(sims[int(sorted_idxs[0])])
        top3 = [float(sims[int(sorted_idxs[i])]) if i < len(sorted_idxs) else 0.0 for i in range(3)]

    if best_sim >= threshold:
        return _ret(best_label, best_sim, retries, top3)

    if not allow_generation:
        if best_sim >= low_threshold:
            return _ret(best_label, best_sim, retries, top3)
        return _ret("Uncategorized", 0.0, retries, [0.0, 0.0, 0.0])

    return classify_file(text, filename, False, retries + 1, cfg)


# File Processing Pipeline

def process_file(file_path, testing=False, allow_generation=True, sorted_dir=None):
    start = time.time()
    filename = os.path.basename(file_path)

    text = extract_text(file_path, fallback=False)
    if not text:
        text = filename.replace("_", " ")

    if not DISABLE_RL:
        policy_id = choose_policy()
        cfg = POLICIES.get(policy_id, {})
    else:
        policy_id = "default"
        cfg = {}

    predicted, sim, retries, top3, manual = classify_file(
        text, filename, allow_generation=allow_generation and cfg.get("ALLOW_GENERATION", True), cfg=cfg
    )

    if not DISABLE_RL:
        interaction_id = f"{filename}|{int(time.time())}"

        event = {
            "interaction_id": interaction_id,
            "event_type": "served",
            "timestamp": int(time.time()),
            "filename": filename,
            "file_path": str(file_path),
            "policy_id": policy_id,
            "predicted_label": predicted,
            "similarity_top1": sim,
            "top3_similarities": top3,
            "manual_labeled": manual,
            "allowed_generation": bool(cfg.get("ALLOW_GENERATION", True)),
            "retries": retries,
            "file_ext": Path(filename).suffix.lstrip("."),
            "text_length": len(text),
            "tfeedback": None
        }

        get_rl_logger().log_event(event)

        def _bg_upload(ev):
            try:
                upload_event(ev)
            except Exception as e:
                print("[supabase] upload failed:", e)

        UPLOAD_EXECUTOR.submit(_bg_upload, event)

    dest_root = Path(sorted_dir) if sorted_dir else BASE_DIR / "sorted"
    dest = dest_root / predicted
    os.makedirs(dest, exist_ok=True)

    if not testing:
        try:
            shutil.move(file_path, dest / filename)
        except Exception as e:
            print("Move error:", e)

    print(f"Processed: {filename} -> {predicted} (sim={sim:.2f})")
