import streamlit as st
from scrapers.google_images import fetch_top_images
from llm.ollama_handler import ask_text, analyze_image
from utils.image_utils import overlay_highlight
import yaml
import os
from PIL import Image
import requests
import base64


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
        
        .mermaid {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        
        .mermaid svg {
            max-width: 100%;
            height: auto;
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

# Add this function at the top of the file

def ensure_png(image_path):
    img = Image.open(image_path)
    png_path = image_path
    if not image_path.lower().endswith('.png'):
        png_path = image_path.rsplit('.', 1)[0] + '.png'
    img.convert('RGB').save(png_path, 'PNG')
    return png_path

def extract_mermaid_code(llm_output):
    # Remove Markdown code block markers and explanations
    lines = llm_output.splitlines()
    code_lines = []
    in_code = False
    for line in lines:
        if line.strip().startswith("flowchart"):
            in_code = True
        if in_code:
            if line.strip().startswith("```"):
                break
            code_lines.append(line)
    return "\n".join(code_lines).strip()

def image_to_mermaid(image_path):
    png_path = ensure_png(image_path)
    # Directly ask the vision LLM to generate Mermaid.js code from the image
    mermaid_prompt = (
        "Convert this VLSI architecture diagram image into a valid Mermaid.js flowchart. "
        "Return only the Mermaid.js code, starting with 'flowchart TD'. "
        "Do not include any explanation or Markdown code block markers."
    )
    mermaid_code_raw = analyze_image(png_path, mermaid_prompt)
    mermaid_code = extract_mermaid_code(mermaid_code_raw)
    if not mermaid_code.strip().startswith("flowchart"):
        print("Mermaid LLM output was not valid code:", mermaid_code_raw)
        return "[Vision LLM to Mermaid failed]", "[Mermaid generation failed]"
    return "[Vision LLM direct to Mermaid]", mermaid_code

# 1️⃣ Stage 1: User prompt to fetch images
if st.session_state.stage == 1:
    user_prompt = st.text_input("Enter your VLSI architecture request (e.g., 'RISC-V pipeline block diagram'):")
    if st.button("Fetch Architectures"):
        with st.spinner("Fetching images…"):
            image_urls = fetch_top_images(user_prompt, cfg["scraping"]["num_images"])
            if image_urls:
                st.session_state.images = image_urls
                st.session_state.stage = 2
                st.rerun()
            else:
                st.error("No images found. Please try a different search term.")

# 2️⃣ Stage 2: Show images to user
elif st.session_state.stage == 2:
    st.subheader("Select one of these architectures")
    
    if not st.session_state.images:
        st.error("No images found. Please try another search term.")
        st.session_state.stage = 1
        st.rerun()
    
    # Create expandable sections for each architecture
    for i, img_info in enumerate(st.session_state.images):
        with st.expander(f"🔍 Architecture Option {i+1}", expanded=True):
            link = img_info["link"]
            desc = img_info["description"]
            st.markdown(f"**Direct Link:** [View Full Image]({link})")
            st.markdown(f"**Description:** {desc}")
            # Try to get LLM description, but don't break the UI if it fails
            try:
                llm_description = ask_text(f"Analyze this VLSI architecture diagram and describe it in 20-30 words: {link}")
                st.markdown(f"**LLM Description:** {llm_description}")
            except Exception as e:
                st.error(f"LLM error: {str(e)}")
            if st.button(f"Select This Architecture", key=f"sel_{i}"):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                        'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
                        'Referer': link,
                    }
                    response = requests.get(link, headers=headers, timeout=10, allow_redirects=True)
                    if response.status_code == 200 and response.content:
                        valid_exts = ['.png', '.jpg', '.jpeg', '.webp']
                        ext = os.path.splitext(link)[-1].split('?')[0].lower()
                        if ext not in valid_exts:
                            ext = '.png'
                        img_path = os.path.join("static", f"selected_arch{ext}")
                        with open(img_path, "wb") as f:
                            f.write(response.content)
                        # Always convert to PNG for downstream processing
                        try:
                            img = Image.open(img_path)
                            png_path = os.path.join("static", "selected_arch.png")
                            img.convert('RGB').save(png_path, "PNG")
                            st.session_state.selected = png_path
                        except Exception as e:
                            st.error(f"Downloaded file is not a valid image: {e}")
                            st.stop()
                        st.session_state.stage = 3
                        st.rerun()
                    else:
                        st.error(f"Failed to download image (status {response.status_code}). Please try another option.")
                except Exception as e:
                    st.error(f"Error saving image: {str(e)}")

# 🔁 Stage 3: Architecture Analysis & Modification
elif st.session_state.stage == 3:
    st.subheader("Architecture Analysis & Conversion")
    
    # First, handle the conversion if not already done
    if "diagram_analysis" not in st.session_state:
        with st.spinner("Converting diagram to Mermaid.js..."):
            text_desc, mermaid_code = image_to_mermaid(st.session_state.selected)
            st.session_state.diagram_analysis = {
                "text": text_desc,
                "mermaid": mermaid_code,
                "current_mermaid": mermaid_code
            }
            st.session_state.show_flow = False  # Don't show flow yet
            st.rerun()
    
    # After conversion is complete, show the code and controls
    if "diagram_analysis" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            img = Image.open(st.session_state.selected)
            st.image(img, caption="Original Architecture", use_column_width=True)
        with col2:
            st.markdown("### 📝 Architecture Components")
            st.write(st.session_state.diagram_analysis["text"])
            st.markdown("### 🧩 Mermaid.js Code")
            mermaid_code = st.text_area(
                "Edit the Mermaid.js code below as needed:",
                value=st.session_state.diagram_analysis["current_mermaid"],
                height=300,
                key="mermaid_code_editor"
            )
            if st.button("Generate Flow"):
                st.session_state.diagram_analysis["current_mermaid"] = mermaid_code
                st.session_state.show_flow = True
                st.rerun()
    
    # Only render the diagram if 'Generate Flow' was pressed
    if st.session_state.get("show_flow"):
        st.markdown("### 🔄 Interactive Diagram")
        mermaid_div = f"""
            <div class="mermaid">
            {st.session_state.diagram_analysis["current_mermaid"]}
            </div>
        """
        html_code = f"""
            <html>
            <body>
                {mermaid_div}
                <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                <script>
                    mermaid.initialize({{
                        startOnLoad: true,
                        theme: 'default',
                        flowchart: {{
                            useMaxWidth: true,
                            htmlLabels: true,
                            curve: 'basis'
                        }}
                    }});
                </script>
            </body>
            </html>
        """
        st.components.v1.html(html_code, height=500)
    
    # LLM-based modification (optional, as before)
    if st.session_state.get("show_flow"):
        st.markdown("---")
        st.subheader("🛠️ Modify Mermaid Diagram")
        mod_prompt = st.text_area(
            "Describe changes to modify the Mermaid diagram:",
            placeholder="Example: Add a cache controller between CPU and memory, or modify the datapath connections..."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Diagram"):
                with st.spinner("Applying changes..."):
                    update_prompt = f"""Modify this Mermaid.js flowchart according to these changes:
                    {mod_prompt}
                    
                    Current diagram:
                    {st.session_state.diagram_analysis["current_mermaid"]}
                    
                    Return ONLY the modified Mermaid.js code."""
                    modified_mermaid = ask_text(update_prompt)
                    st.session_state.diagram_analysis["current_mermaid"] = modified_mermaid
                    st.rerun()
        with col2:
            if st.button("Finalize Design"):
                st.session_state.stage = 5
                st.rerun()
        # Show modification history
        if st.session_state.modifications:
            st.markdown("---")
            with st.expander("📋 Modification History", expanded=False):
                for i, (prompt, _) in enumerate(st.session_state.modifications):
                    st.text(f"{i+1}. {prompt}")

# ✅ Final Download
elif st.session_state.stage == 5:
    st.subheader("🎉 Your final architecture:")
    st.image(st.session_state.selected, use_column_width=True)
    with open(st.session_state.selected, "rb") as f:
        st.download_button("Download Image", f, file_name="modified_architecture.png", mime="image/png")
