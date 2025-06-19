import streamlit as st
from scrapers.google_images import fetch_top_images
from llm.ollama_handler import ask_text, analyze_image
from utils.image_utils import overlay_highlight
import yaml
import os

cfg = yaml.safe_load(open("config.yml"))

st.set_page_config(page_title="VLSI Architecture Designer")
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
            imgs = fetch_top_images(user_prompt, cfg["scraping"]["num_images"])
            st.session_state.images = imgs
            st.session_state.stage = 2
            st.rerun()

# 2️⃣ Stage 2: Show images to user
elif st.session_state.stage == 2:
    st.subheader("Select one of these architectures")
    valid_images = [img for img in st.session_state.images if os.path.exists(img)]
    if not valid_images:
        st.error("No valid images found. Please try another search.")
        st.session_state.stage = 1
        st.rerun()
        
    cols = st.columns(len(valid_images))
    for i, img_path in enumerate(valid_images):
        with cols[i]:
            try:
                st.image(img_path, use_column_width=True)
                if st.button(f"Select {i+1}", key=f"sel_{i}"):
                    st.session_state.selected = img_path
                    st.session_state.stage = 3
                    st.rerun()
            except Exception as e:
                st.error(f"Error displaying image {i+1}")

# 🔁 Modification Loop
elif st.session_state.stage in (3, 4):
    st.subheader("Modify the selected diagram")
    st.image(st.session_state.selected, caption="Current Architecture", use_column_width=True)
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
