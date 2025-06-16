# app.py
import streamlit as st
import os

# Import modules
from scraper import search_and_download_image
from vlm import query_vlm
from utils import ensure_assets_dir

# Ensure assets directory exists
ensure_assets_dir()

st.set_page_config(page_title="VLSI Architecture Expert", layout="centered")
st.title("🔍 VLSI Architecture Expert Assistant")
st.markdown("Ask for an architecture diagram, and get it modified based on your prompt.")

# Input from user
query = st.text_input("Enter VLSI architecture name (e.g., RISC-V CPU block diagram):")

if st.button("Fetch Image"):
    with st.spinner("Fetching image..."):
        try:
            image_path = search_and_download_image(query)
            st.session_state.image_path = image_path
            st.success("Image fetched!")
            st.image(image_path, caption="Fetched Architecture", use_column_width=True)
        except Exception as e:
            st.error(f"Error fetching image: {e}")

if "image_path" in st.session_state:
    st.image(st.session_state.image_path, caption="Current Architecture", use_column_width=True)

    user_prompt = st.text_area("Enter your modification request:")
    if st.button("Generate Modified Architecture"):
        if not user_prompt.strip():
            st.warning("Please enter a modification prompt.")
        else:
            with st.spinner("Analyzing image and generating response..."):
                result = query_vlm(st.session_state.image_path, user_prompt)
                st.markdown("### ✅ Modified Architecture Description:")
                st.markdown(result)