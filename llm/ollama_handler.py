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

def diagram_to_mermaid(img_path):
    """Convert diagram image to Mermaid.js format using LLM"""
    with open(img_path, "rb") as f:
        image_data = f.read()
    b64_img = base64.b64encode(image_data).decode()

    # First get textual description
    diagram_prompt = """Analyze this block diagram and describe the components and their connections 
    in detail. Focus on the flow and relationships between blocks."""
    
    payload = {
        "model": cfg["ollama"]["vision_model"],
        "prompt": diagram_prompt,
        "images": [b64_img],
        "stream": False
    }
    response = requests.post(VISION_URL, json=payload)
    diagram_text = response.json()["response"]
    
    # Convert text to Mermaid
    mermaid_prompt = f"""Convert this block diagram description into Mermaid.js flowchart syntax.
    Use appropriate flowchart symbols and connections.
    Description: {diagram_text}
    
    Return only the Mermaid.js code without any explanation."""
    
    payload = {
        "model": cfg["ollama"]["text_model"],
        "prompt": mermaid_prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return diagram_text, response.json()["response"]

def image_to_mermaid(img_path):
    """Convert image to Mermaid.js diagram using llava model"""
    try:
        with open(img_path, "rb") as f:
            image_data = f.read()
        b64_img = base64.b64encode(image_data).decode()

        # First, get detailed analysis from llava
        vision_prompt = """Analyze this VLSI/hardware architecture diagram.\nIdentify:\n1. Main components and blocks including their names\n2. Connections and data flow including their names\n3. Control signals and interfaces including their names\n4. Hierarchy of components including their names\n5. only explain blocks strectures and connections as it is names mention in that blocks,dont give any explanantion.\nProvide a detailed structural description."""

        vision_payload = {
            "model": "llava",
            "prompt": vision_prompt,
            "images": [b64_img],
            "stream": False
        }
        response = requests.post(VISION_URL, json=vision_payload)
        analysis = response.json()["response"]

        # Then convert to Mermaid.js
        mermaid_prompt = (
            "Convert the following VLSI architecture description into a valid Mermaid.js flowchart. "
            "Return only the Mermaid.js code, starting with 'flowchart TD' or 'flowchart LR'. "
            "Do not include any explanation or Markdown code block markers.\n\n"
            f"Description:\n{analysis}"
        )
        mermaid_code_raw = ask_text(mermaid_prompt)
        return analysis, mermaid_code_raw
    except Exception as e:
        print(f"Error in image_to_mermaid: {str(e)}")
        return "Error analyzing image", "graph TD\nA[Error] --> B[Failed to process image]"


