from google import genai
from google.genai import types
from google.genai.errors import APIError
import json
from dotenv import load_dotenv
import os
from pathlib import Path
import time
import re
from datetime import datetime
from pydantic import BaseModel, Field

load_dotenv()

# API Client Configuration
client = genai.Client(api_key=os.getenv("API_KEY"))
MODEL = "gemini-2.0-flash"

MAX_RETRIES = 5
DEFAULT_BACKOFF = 5 

# Data Schemas
class FolderClassification(BaseModel):
    folder_label: str = Field(
        description="A concise, 1-2 word BROAD category label (e.g., Physics, Finance)."
    )
    description: str = Field(
        description="A dense, comma-separated list of 20-30 synonyms, sub-topics, and related vocabulary."
    )
    keywords: str = Field(
        description="A comma-separated list of 8-12 broad search keywords."
    )

class MergedMetadata(BaseModel):
    merged_description: str = Field(
        description="A single, consolidated description containing a dense list of sub-topics and synonyms from both inputs."
    )
    merged_keywords: str = Field(
        description="A single, comma-separated string of unique, high-value keywords combining both lists without duplicates."
    )

# --- HELPER: SMART RETRY LOGIC ---
def extract_retry_delay(error_message: str) -> float:
    """
    Parses the API error message to find the exact required wait time.
    Example text: "Please retry in 59.849540901s."
    """
    # Regex finds numbers like 4.36 or 59.8 followed explicitly by 's'
    match = re.search(r"retry in (\d+(\.\d+)?)s", error_message)
    if match:
        return float(match.group(1))
    return 0.0

def generate_with_retry(prompt: str, response_schema: type[BaseModel], temperature: float = 0.5):
    """
    Handles API calls with strict adherence to the 'Retry-After' time provided by Google.
    """
    current_backoff = DEFAULT_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=temperature,
                )
            )
            
            # Return parsed object if available, else parse text manually
            if response.parsed:
                return response.parsed
            return response_schema.model_validate_json(response.text)

        except APIError as e:
            if e.code == 429:
                print(f"Rate limit exceeded (Attempt {attempt}/{MAX_RETRIES})")
                
                # 1. Extract exact Google wait time
                wait_time = extract_retry_delay(e.message)
                
                # 2. Fallback if regex fails
                if wait_time == 0:
                    wait_time = current_backoff
                    current_backoff *= 2 # Exponential backoff for unknown delays
                else:
                    wait_time += 1.5 # Add 1.5s safety buffer

                print(f"    Google requested wait: {wait_time:.2f}s")
                print(f"    Sleeping until: {datetime.fromtimestamp(time.time() + wait_time).strftime('%H:%M:%S')}")
                
                time.sleep(wait_time)
                print("    Resuming...")
            
            elif e.code == 404:
                print(f"Error: Model '{MODEL}' unavailable.")
                return None
            
            else:
                print(f"API Error: {e}")
                time.sleep(current_backoff)
                current_backoff *= 2

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    print("Generation failed after maximum retries.")
    return None


def merge_folder_metadata(folder_label, old_desc, old_kw, new_desc, new_kw):
    prompt = f"""You are an expert semantic data organizer. MERGE metadata for category: "{folder_label}".

--- INPUT DATA ---
Existing Description: {old_desc}
Existing Keywords: {old_kw}

New Description: {new_desc}
New Keywords: {new_kw}

--- RULES ---
1. Output `merged_description` as a **dense, comma-separated list**. Merge synonyms.
2. Output `merged_keywords` as a **comma-separated list**. Remove duplicates.
3. Preserve all concepts from Existing metadata.
"""
    
    result: MergedMetadata = generate_with_retry(
        prompt=prompt, 
        response_schema=MergedMetadata, 
        temperature=0.2
    )

    if result:
        return result.model_dump()
    
    return {
        "merged_description": f"{old_desc}, {new_desc}",
        "merged_keywords": f"{old_kw}, {new_kw}"
    }


def generate_folder_label(target_text: str, forced_label: str = None):
    LABELS_FILE = Path("folder_labels.json")
    
    existing_labels_content = "{}"
    if LABELS_FILE.exists():
        try:
            with open(LABELS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    existing_labels_content = content
        except Exception:
            pass

    if forced_label:
        prompt = f"""You are an expert file organization system.
The user has MANUALLY assigned the label "{forced_label}".
Generate description and keywords for "{forced_label}" based on the document below.

--- DOCUMENT ---
{target_text}
"""
    else:
        prompt = f"""Analyze the document and generate a classification.

--- BANNED WORDS ---
"project", "assignment", "pdf", "file", "report", "presentation".

--- EXISTING LABELS ---
{existing_labels_content}

--- RULES ---
1. Use existing labels if the content fits the broad category.
2. Prefer academic labels (Maths, Physics, History, etc.).
3. Distinct subjects must remain separate.

--- DOCUMENT ---
{target_text}
"""

    result: FolderClassification = generate_with_retry(
        prompt=prompt, 
        response_schema=FolderClassification, 
        temperature=0.5
    )

    if not result:
        return False

    new_label = result.folder_label
    new_desc = result.description
    new_keywords_str = result.keywords

    try:
        mode = "r+" if LABELS_FILE.exists() else "w+"
        with open(LABELS_FILE, mode, encoding="utf-8") as f:
            try:
                folder_data = json.load(f)
            except json.JSONDecodeError:
                folder_data = {}

            if new_label not in folder_data:
                folder_data[new_label] = f"{new_desc} Keywords: {new_keywords_str}"
                print(f"Generated new folder label: {new_label}")
            else:
                print(f"Label '{new_label}' exists. Merging metadata...")
                existing_full_text = folder_data[new_label]
                
                if " Keywords: " in existing_full_text:
                    existing_desc, existing_kw_str = existing_full_text.split(" Keywords: ", 1)
                else:
                    existing_desc = existing_full_text
                    existing_kw_str = ""

                merged_data = merge_folder_metadata(
                    folder_label=new_label,
                    old_desc=existing_desc,
                    old_kw=existing_kw_str,
                    new_desc=new_desc,
                    new_kw=new_keywords_str
                )

                final_desc = merged_data["merged_description"]
                final_kws = merged_data["merged_keywords"]
                
                folder_data[new_label] = f"{final_desc} Keywords: {final_kws}"

            f.seek(0)
            json.dump(folder_data, f, indent=2)
            f.truncate()

        return result.model_dump()

    except Exception as e:
        print(f"An error occurred while updating JSON: {e}")
        return False