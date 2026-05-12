import base64
import requests
import re

# --- CONFIG ---
MODEL_NAME = "moondream:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"


def encode_image_base64(image_path: str) -> str:

    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_prompt() -> str:
    return "Identify important objects, obstacles, and hazards in this image with their locations. Keep it brief and direct."


def query_moondream(image_path: str, prompt: str) -> str:

    # Encode image
    img_b64 = encode_image_base64(image_path)
    
    # Build payload with optimized parameters
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [img_b64],
        "stream": False,
        "options": {
            "temperature": 0.5,      # Lebih konsisten
            "num_predict": 60,       # Target 50-70 kata
            "top_k": 20,             # Lebih fokus
            "top_p": 0.87,           # Kurangi variasi
        }
    }
    
    print(f"[Moondream] Querying {MODEL_NAME}...")
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    
    answer = data.get("response", "").strip()
    return answer


def clean_output_for_tts(answer: str) -> str:

    txt = answer.replace("\n", " ").strip()
    
    # Remove leading spaces
    txt = txt.lstrip()
    
    # Remove "Object 1:", "Object 2:", etc
    txt = re.sub(r'^Object\s+\d+:\s*', '', txt, flags=re.IGNORECASE)
    txt = re.sub(r'\.\s+Object\s+\d+:\s*', '. ', txt, flags=re.IGNORECASE)
    
    # Remove numbering "1.", "2.", "3."
    txt = re.sub(r'^\d+\.\s*', '', txt)
    txt = re.sub(r'\.\s+\d+\.\s*', '. ', txt)
    
    # Capitalize first letter
    if txt:
        txt = txt[0].upper() + txt[1:]
    
    # Cleanup multiple spaces
    txt = " ".join(txt.split())
    
    # Fix incomplete sentences
    if txt and not txt[-1] in ['.', '!', '?']:
        last_period = txt.rfind('.')
        if last_period > 0:
            txt = txt[:last_period + 1]
        else:
            txt += "."
    
    # Fallback if too short
    if len(txt) < 10 or len(txt.split()) < 3:
        return "Obstacles detected ahead. Please proceed with caution."
    
    # Ensure ending punctuation
    if not txt.endswith("."):
        txt += "."
    
    return txt
