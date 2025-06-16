# app.py
import streamlit as st
import os
import cv2
from PIL import Image
import numpy as np

# Import modules
from scraper import search_and_download_image
from vlm import query_vlm
from utils import ensure_assets_dir

# Ensure assets directory exists
ensure_assets_dir()

st.set_page_config(page_title="VLSI Architecture Expert", layout="centered")
st.title("🔍 VLSI Architecture Expert Assistant")
st.markdown("Ask for an architecture diagram, and get it modified based on your prompt.")

def modify_image(image_path, modifications):
    # Load image using PIL
    img = Image.open(image_path)
    # Convert to numpy array for OpenCV operations
    img_array = np.array(img)
    
    # Basic image modifications based on keywords
    if "highlight" in modifications.lower():
        # Add brightness
        img_array = cv2.convertScaleAbs(img_array, alpha=1.2, beta=10)
    if "darker" in modifications.lower():
        # Reduce brightness
        img_array = cv2.convertScaleAbs(img_array, alpha=0.8, beta=-10)
    
    # Convert back to PIL Image
    modified_img = Image.fromarray(img_array)
    modified_path = "assets/modified_arch.png"
    modified_img.save(modified_path)
    return modified_path

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
                # Get VLM description
                result = query_vlm(st.session_state.image_path, user_prompt)
                st.markdown("### ✅ Modified Architecture Description:")
                st.markdown(result)
                
                # Modify image based on prompt
                modified_image_path = modify_image(st.session_state.image_path, user_prompt)
                st.markdown("### Preview of Modified Image:")
                st.image(modified_image_path, caption="Modified Architecture", use_column_width=True)
                
                # Add confirmation button
                if st.button("Confirm and Download Modified Image"):
                    try:
                        # Prepare download button
                        with open(modified_image_path, "rb") as file:
                            btn = st.download_button(
                                label="Download Modified Architecture",
                                data=file,
                                file_name="modified_architecture.png",
                                mime="image/png"
                            )
                        st.success("Image downloaded successfully!")
                    except Exception as e:
                        st.error(f"Error downloading image: {e}")