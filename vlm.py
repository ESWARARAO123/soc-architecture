# vlm.py
import base64
import requests

OLLAMA_API_URL = "http://localhost:11434/api/chat"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def query_vlm(image_path, prompt):
    image_b64 = encode_image(image_path)

    payload = {
        "model": "llava",
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64]
            }
        ],
        "stream": False
    }

    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json()['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"