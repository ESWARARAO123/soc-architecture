import streamlit as st
from scrapers.google_images import fetch_top_images
from llm.ollama_handler import ask_text, analyze_image
from utils.image_utils import overlay_highlight
import yaml
import os
from PIL import Image
import requests
from io import BytesIO
from urllib.parse import urlparse, parse_qs
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus

cfg = yaml.safe_load(open("config.yml"))

st.set_page_config(page_title="VLSI Architecture Designer", layout="wide")

# Add custom CSS for better image display
st.markdown("""
    <style>
        .stImage > img {
            image-rendering: -webkit-optimize-contrast !important;
            image-rendering: crisp-edges !important;
            max-width: 800px !important;
            width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
            padding: 8px !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            margin: 10px auto !important;
            background: white !important;
        }
        .stButton > button {
            margin-top: 15px !important;
            width: 100% !important;
            height: 40px !important;
            border-radius: 8px !important;
        }
        [data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            padding: 15px !important;
            background: #f8f9fa !important;
            border-radius: 12px !important;
            margin: 5px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 VLSI Architecture Designer")

if "stage" not in st.session_state:
    st.session_state.update({
        "stage": 1,
        "images": [],
        "selected": None,
        "modifications": []
    })

# 1️⃣ Stage 1: User prompt to fetch images
if st.session_state.stage == 1:
    user_prompt = st.text_input("Enter your VLSI architecture request (e.g., 'RISC-V pipeline block diagram'):")
    if st.button("Fetch Architectures"):
        with st.spinner("Fetching images…"):
            image_urls = fetch_top_images(user_prompt, 5)  # Use your function!
            if image_urls:
                st.session_state.images = image_urls
                st.session_state.stage = 2
                st.rerun()
            else:
                st.error("No images found. Please try a different search term.")

# 2️⃣ Stage 2: Show image links and descriptions to user
elif st.session_state.stage == 2:
    st.subheader("Select one of these architectures ")
    for i, item in enumerate(st.session_state.images):
        link = item["link"]
        desc = item["description"]
        st.markdown(f"**[{i+1}. View Image Link]({link})**")
        st.write(desc)
        if st.button(f"Select {i+1}", key=f"sel_{i}"):
            # Download the image and save locally
            response = requests.get(link)
            if response.status_code == 200:
                os.makedirs("static", exist_ok=True)
                img_path = os.path.join("static", f"selected_arch.png")
                with open(img_path, "wb") as f:
                    f.write(response.content)
                st.session_state.selected = img_path
                st.session_state.stage = 3
                st.rerun()
            else:
                st.error("Failed to download image. Please try another one.")

# 🔁 Modification Loop
elif st.session_state.stage in (3, 4):
    st.subheader("Modify the selected diagram")
    img = Image.open(st.session_state.selected)
    st.image(img, caption="Current Architecture", use_column_width="auto")
    mod_prompt = st.text_input("Describe modification (e.g., 'remove the ALU block and add cache block'):")
    if st.button("Apply Modification"):
        with st.spinner("Applying modification…"):
            prompt = f"Diagram modification instructions:\n{mod_prompt}"
            analysis = analyze_image(st.session_state.selected, prompt)
            boxes = []  # parse from analysis if bounding boxes returned
            new_img = overlay_highlight(st.session_state.selected, boxes)
            st.session_state.selected = new_img
            st.session_state.modifications.append((mod_prompt, analysis))
            st.session_state.stage = 4
            st.rerun()
    if st.session_state.modifications:
        st.markdown("**Modification history:**")
        for i, (mp, an) in enumerate(st.session_state.modifications):
            st.write(f"#{i+1} — ✏️ *Prompt:* **{mp}**  ➜ *LLM said:* {an}")
    if st.button("Finalize & Download"):
        st.session_state.stage = 5
        st.rerun()

# ✅ Final Download
elif st.session_state.stage == 5:
    st.subheader("🎉 Your final architecture:")
    st.image(st.session_state.selected, use_column_width=True)
    with open(st.session_state.selected, "rb") as f:
        st.download_button("Download Image", f, file_name="modified_architecture.png", mime="image/png")
