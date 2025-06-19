import requests
from PIL import Image
import io
import yaml
import base64

cfg = yaml.safe_load(open("config.yml"))

OLLAMA_URL = "http://localhost:11434/api/generate"
VISION_URL = "http://localhost:11434/api/generate"

def ask_text(prompt):
    payload = {
        "model": cfg["ollama"]["text_model"],
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"]

def analyze_image(img_path, prompt):
    with open(img_path, "rb") as f:
        image_data = f.read()
    b64_img = base64.b64encode(image_data).decode()

    payload = {
        "model": cfg["ollama"]["vision_model"],
        "prompt": prompt,
        "images": [b64_img],
        "stream": False
    }
    response = requests.post(VISION_URL, json=payload)
    return response.json()["response"]
