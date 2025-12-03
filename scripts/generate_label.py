from google import genai
from google.genai.errors import APIError
import json
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("API_KEY"))
MODEL = "gemini-2.5-flash"

schema = {
    "type": "object",
    "properties": {
        "folder_label": {
            "type": "string",
            "description": "A High-Level Universal Category (e.g., Sports, Business, Technology, Politics, Science)."
        },
        "description": {
            "type": "string",
            "description": "A Universal Definition of the category. It must NOT describe the specific document, but rather the ENTIRE DOMAIN the document belongs to."
        },
        "keywords": {
            "type": "string",
            "description": "A list of 15 broad domain keywords."
        }
    },
    "required": ["folder_label", "description", "keywords"]
}

merge_schema = {
    "type": "object",
    "properties": {
        "merged_description": {
            "type": "string",
            "description": "A broadened Universal Definition that encompasses both scopes."
        },
        "merged_keywords": {
            "type": "string",
            "description": "A combined list of high-level domain keywords."
        }
    },
    "required": ["merged_description", "merged_keywords"]
}

def merge_folder_metadata(folder_label, old_desc, old_kw, new_desc, new_kw):
    # If we are merging, we want to make the definition BROADER, not more specific.
    prompt = f"""You are a Dictionary Editor.
    
    Category: "{folder_label}"
    Definition A: "{old_desc}"
    Definition B: "{new_desc}"
    
    Task: Create a **Master Definition** that includes the scope of both A and B. 
    - It must be abstract and generic.
    - Example: If A is "Stock Prices" and B is "Tax Audits", the Master is "Financial documentation including market analysis, fiscal compliance, and asset valuation."
    """

    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json", "response_schema": merge_schema}
        )
        return json.loads(res.text)
    except:
        return {"merged_description": old_desc, "merged_keywords": old_kw}

def generate_folder_label(target_text: str):
    try:
        with open("folder_labels.json", "r", encoding="utf-8") as f:
            existing = f.read()
            existing_labels_content = existing if existing.strip() else "{}"
    except:
        existing_labels_content = "{}"

    prompt = f"""You are an expert Ontology Architect. Classify this document into a Universal Top-Level Domain.

--- CRITICAL INSTRUCTION: DE-COUPLE CONTENT ---
You must classify the document, but your Description MUST NOT describe the document's specific events. 
It must describe the **CATEGORY** itself.

**Example 1 (Boxing Match File):**
*   BAD Description: "A report on the Tyson vs Paul boxing match and knockout results." (Too specific)
*   GOOD Description: "Competitive athletic events, professional sports leagues, tournament standings, player statistics, and match results." (Universal - Fits Football too!)

**Example 2 (Gold Mining Acquisition File):**
*   BAD Description: "Documents about Goldcorp buying Wheaton River Minerals."
*   GOOD Description: "Corporate finance, mergers and acquisitions, stock market analysis, investment banking, and industry consolidation reports." (Universal - Fits Airlines too!)

**Example 3 (Hurricane Ivan File):**
*   BAD Description: "Weather reports tracking Hurricane Ivan."
*   GOOD Description: "Environmental science, meteorological forecasting, climate studies, natural disaster tracking, and atmospheric phenomena."

--- TARGET CATEGORIES ---
Aim to use these 5-6 buckets if applicable:
1. **Business** (Finance, Econ, Industry)
2. **Politics** (Gov, International Relations, Law)
3. **Sports** (All athletics)
4. **Technology** (Computers, AI, Gadgets)
5. **Science** (Health, Bio, Space, Environment)
6. **Arts** (Movies, Music, Culture)

--- EXISTING LABELS ---
{existing_labels_content}

--- USER DOCUMENT ---
{target_text}
"""

    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json", "response_schema": schema, "temperature": 0.3}
        )
        response = json.loads(res.text)
        
        # Save logic (Standard)
        new_label = response.get("folder_label")
        new_desc = response.get("description")
        new_kw = response.get("keywords")
        
        with open("folder_labels.json", "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
            
            if new_label not in data:
                data[new_label] = f"{new_desc} Keywords: {new_kw}"
                print(f"Generated Universal Label: {new_label}")
            else:
                print(f"Merging into Universal Label: {new_label}...")
                existing_full = data[new_label]
                if " Keywords: " in existing_full:
                    e_desc, e_kw = existing_full.split(" Keywords: ", 1)
                else:
                    e_desc, e_kw = existing_full, ""
                
                merged = merge_folder_metadata(new_label, e_desc, e_kw, new_desc, new_kw)
                data[new_label] = f"{merged.get('merged_description')} Keywords: {merged.get('merged_keywords')}"

            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

        return response
    except Exception as e:
        print(f"Error: {e}")
        return False